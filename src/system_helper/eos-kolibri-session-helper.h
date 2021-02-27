/* eos-kolibri-session-helper.h
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

#ifndef EOS_KOLIBRI_SESSION_HELPER_H
#define EOS_KOLIBRI_SESSION_HELPER_H

#include "eos-kolibri-dbus.h"

#include <glib-object.h>


G_BEGIN_DECLS

#define EOS_KOLIBRI_TYPE_SESSION_HELPER eos_kolibri_session_helper_get_type ()
G_DECLARE_FINAL_TYPE (EosKolibriSessionHelper, eos_kolibri_session_helper, EOS_KOLIBRI, SESSION_HELPER, GObject)
EosKolibriSessionHelper *eos_kolibri_session_helper_new (void);

EosKolibriDBusKolibriSessionHelper *eos_kolibri_session_helper_get_session_helper_proxy (EosKolibriSessionHelper *self);

void eos_kolibri_session_helper_export_dbus_object (EosKolibriSessionHelper *self, GDBusObjectManagerServer *manager, gchar *path);

G_END_DECLS

#endif
