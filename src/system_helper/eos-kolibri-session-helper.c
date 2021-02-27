/* eos-kolibri-session-helper.c
 *
 * Copyright 2021 Endless OS Foundation
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * Author: Dylan McCall <dylan@endlessos.org>
 */

#include "config.h"
#include "eos-kolibri-dbus.h"
#include "eos-kolibri-share-directory-context.h"

#include <fcntl.h>
#include <gio/gunixfdlist.h>

static const char *REVOKEFS_FUSE_BIN = LIBEXECDIR"/revokefs-fuse";

struct _EosKolibriSessionHelper
{
  GObject parent_instance;

  EosKolibriDBusKolibriSessionHelper *session_helper_proxy;
  EosKolibriDBusKolibriSystemHelper *system_helper_proxy;
};

G_DEFINE_TYPE (EosKolibriSessionHelper, eos_kolibri_session_helper, G_TYPE_OBJECT)

static void
handle_share_directory_kolibri_system_helper_get_revokefs_backend_fd_result_func (GObject      *source_object,
                                                                                  GAsyncResult *res,
                                                                                  gpointer      user_data)
{
  EosKolibriDBusKolibriSystemHelper *system_helper_proxy = EOS_KOLIBRI_DBUS_KOLIBRI_SYSTEM_HELPER (source_object);
  EosKolibriShareDirectoryContext *context = EOS_KOLIBRI_SHARE_DIRECTORY_CONTEXT (user_data);

  g_autoptr(GError) error = NULL;
  g_autoptr(GVariant) backend_fd_index = NULL;
  g_autoptr(GUnixFDList) fd_list = NULL;
  g_autoptr(GSubprocessLauncher) launcher = NULL;
  g_autoptr(GSubprocess) backend_subprocess = NULL;
  int backend_socket_fd;

  eos_kolibri_dbus_kolibri_system_helper_call_get_revokefs_backend_fd_finish (system_helper_proxy,
                                                                              &backend_fd_index,
                                                                              &fd_list,
                                                                              res,
                                                                              &error);

  if (error)
  {
    eos_kolibri_share_directory_context_return_error_literal (context,
                                                              G_DBUS_ERROR,
                                                              G_DBUS_ERROR_FAILED,
                                                              "Error calling GetRevokeFs in KolibriSystemHelper");
    return;
  }

  backend_socket_fd = g_unix_fd_list_get (fd_list,
                                          g_variant_get_handle (backend_fd_index),
                                          &error);

  if (error)
  {
    eos_kolibri_share_directory_context_return_error_literal (context,
                                                              G_DBUS_ERROR,
                                                              G_DBUS_ERROR_FAILED,
                                                              "Error getting file descriptor from KolibriSystemHelper");
    return;
  }

  launcher = g_subprocess_launcher_new (G_SUBPROCESS_FLAGS_NONE);
  g_subprocess_launcher_take_fd (launcher, backend_socket_fd, 3);
  // launcher owns backend_socket_fd

  fcntl (backend_socket_fd, F_SETFD, FD_CLOEXEC);
  backend_subprocess = g_subprocess_launcher_spawn (launcher,
                                                    &error,
                                                    REVOKEFS_FUSE_BIN,
                                                    "--backend",
                                                    "--socket=3",
                                                    eos_kolibri_share_directory_context_get_source_dir (context),
                                                    NULL);

  if (error)
  {
    eos_kolibri_share_directory_context_return_error_literal (context,
                                                              G_DBUS_ERROR,
                                                              G_DBUS_ERROR_FAILED,
                                                              "Failed to launch revokefs-fuse process");
    return;
  }

  eos_kolibri_share_directory_context_complete (context);
}

static gboolean
handle_share_directory (EosKolibriDBusKolibriSessionHelper  *session_helper_proxy,
                        GDBusMethodInvocation               *invocation,
                        // GUnixFDList                         *in_fd_list,
                        gchar                               *source_dir,
                        EosKolibriSessionHelper             *session_helper)
{
  g_autoptr(EosKolibriShareDirectoryContext) context = NULL;

  context = eos_kolibri_share_directory_context_new (session_helper,
                                                     session_helper_proxy,
                                                     invocation,
                                                     source_dir);

  eos_kolibri_dbus_kolibri_system_helper_call_get_revokefs_backend_fd (session_helper->system_helper_proxy,
                                                                       source_dir,
                                                                       NULL,
                                                                       NULL,
                                                                       handle_share_directory_kolibri_system_helper_get_revokefs_backend_fd_result_func,
                                                                       g_object_ref (context));

  return TRUE;
}

static void
eos_kolibri_session_helper_dispose (GObject *gobject)
{
  EosKolibriSessionHelper *self = EOS_KOLIBRI_SESSION_HELPER (gobject);
  if (self->session_helper_proxy)
    g_object_unref (self->session_helper_proxy);
  if (self->system_helper_proxy)
    g_object_unref (self->system_helper_proxy);
  G_OBJECT_CLASS (eos_kolibri_session_helper_parent_class)->dispose (gobject);
}

static void
eos_kolibri_session_helper_finalize (GObject *gobject)
{
  // EosKolibriSessionHelper *self = EOS_KOLIBRI_SESSION_HELPER (gobject);
  G_OBJECT_CLASS (eos_kolibri_session_helper_parent_class)->finalize (gobject);
}

static void
eos_kolibri_session_helper_class_init (EosKolibriSessionHelperClass *klass)
{
  GObjectClass *object_class = G_OBJECT_CLASS (klass);
  object_class->dispose = eos_kolibri_session_helper_dispose;
  object_class->finalize = eos_kolibri_session_helper_finalize;
}

static void
eos_kolibri_session_helper_init (EosKolibriSessionHelper *self)
{
  self->session_helper_proxy = NULL;
  self->system_helper_proxy = NULL;
}

EosKolibriSessionHelper *
eos_kolibri_session_helper_new (void)
{
  EosKolibriSessionHelper *self = g_object_new (EOS_KOLIBRI_TYPE_SESSION_HELPER, NULL);
  self->session_helper_proxy = eos_kolibri_dbus_kolibri_session_helper_skeleton_new ();
  self->system_helper_proxy = eos_kolibri_dbus_kolibri_system_helper_proxy_new_for_bus_sync (G_BUS_TYPE_SYSTEM,
                                                                                             G_DBUS_PROXY_FLAGS_NONE,
                                                                                             "org.endlessos.KolibriSystemHelper",
                                                                                             "/org/endlessos/KolibriSystemHelper/Core",
                                                                                             NULL,
                                                                                             NULL);

  g_signal_connect_object (self->session_helper_proxy,
                           "handle-share-directory",
                           G_CALLBACK (handle_share_directory),
                           self,
                           0);

  return self;
}

EosKolibriDBusKolibriSessionHelper *
eos_kolibri_session_helper_get_session_helper_proxy (EosKolibriSessionHelper *self)
{
  return self->session_helper_proxy;
}

void
eos_kolibri_session_helper_export_dbus_object (EosKolibriSessionHelper *self, GDBusObjectManagerServer *manager, gchar *path)
{
  g_autoptr(EosKolibriDBusObjectSkeleton) object = NULL;
  object = eos_kolibri_dbus_object_skeleton_new (path);
  eos_kolibri_dbus_object_skeleton_set_kolibri_session_helper (object, self->session_helper_proxy);
  g_dbus_object_manager_server_export (manager, G_DBUS_OBJECT_SKELETON (object));
}

