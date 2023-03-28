/* eos-kolibri-share-directory-context.h
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

#ifndef EOS_KOLIBRI_SHARE_DIRECTORY_CONTEXT_H
#define EOS_KOLIBRI_SHARE_DIRECTORY_CONTEXT_H

#include "eos-kolibri-dbus.h"
#include "eos-kolibri-session-helper.h"

#include <glib-object.h>


G_BEGIN_DECLS

#define EOS_KOLIBRI_TYPE_SHARE_DIRECTORY_CONTEXT eos_kolibri_share_directory_context_get_type ()
G_DECLARE_FINAL_TYPE (EosKolibriShareDirectoryContext, eos_kolibri_share_directory_context, EOS_KOLIBRI, SHARE_DIRECTORY_CONTEXT, GObject)
EosKolibriShareDirectoryContext *eos_kolibri_share_directory_context_new (EosKolibriSessionHelper             *session_helper,
                                                                          EosKolibriDBusKolibriSessionHelper  *skeleton,
                                                                          GDBusMethodInvocation               *invocation,
                                                                          gchar                               *source_dir);

void eos_kolibri_share_directory_context_complete (EosKolibriShareDirectoryContext *self);
void eos_kolibri_share_directory_context_return_error_literal (EosKolibriShareDirectoryContext *self,
                                                               GQuark domain,
                                                               gint code,
                                                               const gchar *message);

gchar *eos_kolibri_share_directory_context_get_source_dir (EosKolibriShareDirectoryContext *self);

G_END_DECLS

#endif
