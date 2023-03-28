/* eos-kolibri-system-helper-main.c
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

static GMainLoop *main_loop = NULL;

static void
on_bus_acquired (GDBusConnection *connection,
                 const char      *name,
                 gpointer         user_data)
{

  GDBusObjectManagerServer *manager = NULL;
  EosKolibriSystemHelper *system_helper = NULL;
  char *path;

  manager = g_dbus_object_manager_server_new ("/org/endlessos/KolibriSystemHelper");

  path = g_strdup ("/org/endlessos/KolibriSystemHelper/Core");
  system_helper = eos_kolibri_system_helper_new ();
  eos_kolibri_system_helper_export_dbus_object (system_helper, manager, path);
  g_free (path);

  g_dbus_object_manager_server_set_connection (manager, connection);
}

static void
on_name_acquired (GDBusConnection *connection,
                  const char      *name,
                  gpointer         user_data)
{}

static void
on_name_lost (GDBusConnection *connection,
              const char      *name,
              gpointer         user_data)
{
  g_main_loop_quit (main_loop);
}

int
main (int argc, char *argv[])
{
  gboolean option_version = FALSE;
  gboolean option_replace = FALSE;
  gboolean option_session = FALSE;
  gint option_idle_timeout = -1;
  const GOptionEntry options[] = {
    { "version", 0, 0, G_OPTION_ARG_NONE, &option_version, "Show program version.", NULL},
    { "replace", 'r', 0, G_OPTION_ARG_NONE, &option_replace,  "Replace old daemon.", NULL },
    { "session", 0, 0, G_OPTION_ARG_NONE, &option_session,  "Connect to the session bus.", NULL },
    { "idle-timeout", 0, 0, G_OPTION_ARG_INT, &option_idle_timeout,  "Idle timeout in seconds.", NULL },
    { NULL }
  };

  guint bus_owner_id;
  GBusType bus_type;
  GBusNameOwnerFlags bus_flags;
  g_autoptr(GOptionContext) context = NULL;
  g_autoptr(GError) error = NULL;

  context = g_option_context_new (NULL);
  g_option_context_set_summary (context, "Kolibri system helper");
  g_option_context_add_main_entries (context, options, NULL);

  if (!g_option_context_parse (context, &argc, &argv, &error))
  {
    g_printerr ("%s: %s", g_get_application_name (), error->message);
    g_printerr ("\n");
    g_printerr ("Try \"%s --help\" for more information.",
                g_get_prgname ());
    g_printerr ("\n");
    return 1;
  }

  if (option_version)
  {
    g_print (PACKAGE_STRING "\n");
    return 0;
  }

  bus_flags = G_BUS_NAME_OWNER_FLAGS_ALLOW_REPLACEMENT;
  if (option_replace)
    bus_flags |= G_BUS_NAME_OWNER_FLAGS_REPLACE;

  bus_type = option_session ? G_BUS_TYPE_SESSION : G_BUS_TYPE_SYSTEM;

  bus_owner_id = g_bus_own_name (bus_type,
                                 "org.endlessos.KolibriSystemHelper",
                                 bus_flags,
                                 on_bus_acquired,
                                 on_name_acquired,
                                 on_name_lost,
                                 NULL,
                                 NULL);

  main_loop = g_main_loop_new (NULL, FALSE);
  g_main_loop_run (main_loop);

  g_bus_unown_name (bus_owner_id);

  return 0;
}

