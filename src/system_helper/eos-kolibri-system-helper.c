/* eos-kolibri-system-helper.c
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

/* FIXME: For this all to work, we also need an selinux module to allow this
 *        program to pass a domain socket over the dbus system bus, like with
 *        flatpak-system-helper:
 *        <https://github.com/flatpak/flatpak/commit/bb46c1dbd63ff4b314836721267a1cf609f23ce8>
 */

#include "config.h"
#include "eos-kolibri-system-helper.h"

#include <fcntl.h>
#include <gio/gunixfdlist.h>
#include <sys/socket.h>

static const char *REVOKEFS_FUSE_BIN = LIBEXECDIR"/revokefs-fuse";

struct _EosKolibriSystemHelper
{
  GObject parent_instance;

  EosKolibriDBusKolibriSystemHelper *system_helper_proxy;
  gchar *mounts_dir;
  GRegex *mount_name_re;
};

G_DEFINE_TYPE (EosKolibriSystemHelper, eos_kolibri_system_helper, G_TYPE_OBJECT)

static gboolean
handle_get_revokefs_backend_fd (EosKolibriDBusKolibriSystemHelper  *system_helper_proxy,
                                GDBusMethodInvocation              *invocation,
                                GUnixFDList                        *in_fd_list,
                                gchar                              *source_dir,
                                EosKolibriSystemHelper             *system_helper)
{
  g_autofree gchar *source_name = NULL;
  g_autofree gchar *target_dir = NULL;
  int sockets[2];
  int backend_socket_fd, fuse_socket_fd;
  g_autoptr(GError) error = NULL;
  g_autoptr(GSubprocessLauncher) launcher = NULL;
  g_autoptr(GSubprocess) fuse_subprocess = NULL;
  g_autoptr(GUnixFDList) out_fd_list = NULL;
  gint out_fd_index;

  source_name = g_regex_replace (system_helper->mount_name_re,
                                 g_path_skip_root (source_dir),
                                 -1,
                                 0,
                                 "-",
                                 0,
                                 &error);
  g_assert_no_error (error);

  target_dir = g_build_filename (system_helper->mounts_dir, source_name, NULL);

  if (g_mkdir_with_parents (target_dir, 0700) != 0)
  {
    g_assert_not_reached ();
  }

  if (socketpair (AF_UNIX, SOCK_SEQPACKET, 0, sockets) != 0)
  {
    g_dbus_method_invocation_return_error (invocation,
                                           G_DBUS_ERROR,
                                           G_DBUS_ERROR_FAILED,
                                           "Failed to create revokefs socket pair");
    return TRUE;
  }

  backend_socket_fd = sockets[0];
  fuse_socket_fd = sockets[1];

  out_fd_list = g_unix_fd_list_new ();
  out_fd_index = g_unix_fd_list_append (out_fd_list, backend_socket_fd, NULL);
  close (backend_socket_fd);

  launcher = g_subprocess_launcher_new (G_SUBPROCESS_FLAGS_NONE);
  g_subprocess_launcher_take_fd (launcher, fuse_socket_fd, 3);
  // launcher owns fuse_socket_fd

  fcntl (fuse_socket_fd, F_SETFD, FD_CLOEXEC);
  fuse_subprocess = g_subprocess_launcher_spawn (launcher,
                                                 &error,
                                                 REVOKEFS_FUSE_BIN,
                                                 "--socket=3",
                                                 source_dir,
                                                 target_dir,
                                                 NULL);

  if (error)
  {
    g_dbus_method_invocation_return_error (invocation,
                                           G_DBUS_ERROR,
                                           G_DBUS_ERROR_FAILED,
                                           "Failed to launch revokefs-fuse process");
    return TRUE;
  }

  eos_kolibri_dbus_kolibri_system_helper_complete_get_revokefs_backend_fd (system_helper_proxy,
                                                                           invocation,
                                                                           out_fd_list,
                                                                           g_variant_new_handle (out_fd_index));

  return TRUE;
}

static void
eos_kolibri_system_helper_dispose (GObject *gobject)
{
  EosKolibriSystemHelper *self = EOS_KOLIBRI_SYSTEM_HELPER (gobject);
  g_free (self->mounts_dir);
  g_free (self->mount_name_re);
  G_OBJECT_CLASS (eos_kolibri_system_helper_parent_class)->dispose (gobject);
}

static void
eos_kolibri_system_helper_finalize (GObject *gobject)
{
  // EosKolibriSystemHelper *self = EOS_KOLIBRI_SYSTEM_HELPER (gobject);
  G_OBJECT_CLASS (eos_kolibri_system_helper_parent_class)->finalize (gobject);
}

static void
eos_kolibri_system_helper_class_init (EosKolibriSystemHelperClass *klass)
{
  GObjectClass *object_class = G_OBJECT_CLASS (klass);
  object_class->dispose = eos_kolibri_system_helper_dispose;
  object_class->finalize = eos_kolibri_system_helper_finalize;
}

static void
eos_kolibri_system_helper_init (EosKolibriSystemHelper *self)
{
  self->mounts_dir = g_strdup (g_get_home_dir ());
  self->mount_name_re = g_regex_new ("[^\\w\\d\\-]", 0, 0, NULL);
}

EosKolibriSystemHelper *
eos_kolibri_system_helper_new (void)
{
  EosKolibriSystemHelper *self = g_object_new (EOS_KOLIBRI_TYPE_SYSTEM_HELPER, NULL);
  self->system_helper_proxy = eos_kolibri_dbus_kolibri_system_helper_skeleton_new ();

  g_signal_connect_object (self->system_helper_proxy,
                           "handle-get-revokefs-backend-fd",
                           G_CALLBACK (handle_get_revokefs_backend_fd),
                           self,
                           0);

  return self;
}

EosKolibriDBusKolibriSystemHelper *
eos_kolibri_system_helper_get_system_helper_proxy (EosKolibriSystemHelper *self)
{
  return self->system_helper_proxy;
}

void
eos_kolibri_system_helper_export_dbus_object (EosKolibriSystemHelper *self, GDBusObjectManagerServer *manager, gchar *path)
{
  g_autoptr(EosKolibriDBusObjectSkeleton) object = NULL;
  object = eos_kolibri_dbus_object_skeleton_new (path);
  eos_kolibri_dbus_object_skeleton_set_kolibri_system_helper (object, self->system_helper_proxy);
  g_dbus_object_manager_server_export (manager, G_DBUS_OBJECT_SKELETON (object));
}
