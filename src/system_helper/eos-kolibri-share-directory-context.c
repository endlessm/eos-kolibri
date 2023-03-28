/* eos-kolibri-share-directory-context.c
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

#include "eos-kolibri-share-directory-context.h"

struct _EosKolibriShareDirectoryContext
{
  GObject parent_instance;

  EosKolibriSessionHelper             *session_helper;
  EosKolibriDBusKolibriSessionHelper  *session_helper_proxy;
  GDBusMethodInvocation               *invocation;
  gchar                               *source_dir;
};

G_DEFINE_TYPE (EosKolibriShareDirectoryContext, eos_kolibri_share_directory_context, G_TYPE_OBJECT)

static void
eos_kolibri_share_directory_context_dispose (GObject *gobject)
{
  EosKolibriShareDirectoryContext *self = EOS_KOLIBRI_SHARE_DIRECTORY_CONTEXT (gobject);
  if (self->session_helper)
    g_object_unref (self->session_helper);
  if (self->session_helper_proxy)
    g_object_unref (self->session_helper_proxy);
  if (self->invocation)
    g_object_unref (self->invocation);
  if (self->source_dir)
    g_free (self->source_dir);
  G_OBJECT_CLASS (eos_kolibri_share_directory_context_parent_class)->dispose (gobject);
}

static void
eos_kolibri_share_directory_context_finalize (GObject *gobject)
{
  // EosKolibriShareDirectoryContext *self = EOS_KOLIBRI_SYSTEM_HELPER (gobject);
  G_OBJECT_CLASS (eos_kolibri_share_directory_context_parent_class)->finalize (gobject);
}

static void
eos_kolibri_share_directory_context_class_init (EosKolibriShareDirectoryContextClass *klass)
{
  GObjectClass *object_class = G_OBJECT_CLASS (klass);
  object_class->dispose = eos_kolibri_share_directory_context_dispose;
  object_class->finalize = eos_kolibri_share_directory_context_finalize;
}

static void
eos_kolibri_share_directory_context_init (EosKolibriShareDirectoryContext *self)
{
  self->session_helper = NULL;
  self->session_helper_proxy = NULL;
  self->invocation = NULL;
  self->source_dir = NULL;
}

EosKolibriShareDirectoryContext *
eos_kolibri_share_directory_context_new (EosKolibriSessionHelper             *session_helper,
                                         EosKolibriDBusKolibriSessionHelper  *session_helper_proxy,
                                         GDBusMethodInvocation               *invocation,
                                         gchar                               *source_dir)
{
  EosKolibriShareDirectoryContext *self = g_object_new (EOS_KOLIBRI_TYPE_SHARE_DIRECTORY_CONTEXT, NULL);
  self->session_helper = g_object_ref (session_helper);
  self->session_helper_proxy = g_object_ref (session_helper_proxy);
  self->invocation = g_object_ref (invocation);
  self->source_dir = g_strdup (source_dir);
  return self;
}

void eos_kolibri_share_directory_context_complete (EosKolibriShareDirectoryContext *self)
{
  eos_kolibri_dbus_kolibri_session_helper_complete_share_directory (self->session_helper_proxy, self->invocation);
}

void eos_kolibri_share_directory_context_return_error_literal (EosKolibriShareDirectoryContext *self,
                                                               GQuark domain,
                                                               gint code,
                                                               const gchar *message)
{
  g_dbus_method_invocation_return_error_literal (self->invocation, domain, code, message);
}

gchar *eos_kolibri_share_directory_context_get_source_dir (EosKolibriShareDirectoryContext *self)
{
  return self->source_dir;
}

