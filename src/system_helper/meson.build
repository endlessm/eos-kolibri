gio_dep = dependency('gio-2.0')
gio_unix_dep = dependency('gio-unix-2.0')
glib_dep = dependency('glib-2.0')
gobject_dep = dependency('gobject-2.0')

system_helper_application_id = 'org.endlessos.KolibriSystemHelper'
session_helper_application_id = 'org.endlessos.KolibriSessionHelper'
package_string = '@0@-@1@'.format(meson.project_name(), meson.project_version())

system_helper_config = configuration_data()
system_helper_config.set_quoted('PACKAGE_STRING', package_string)
system_helper_config.set_quoted('SYSTEM_HELPER_APPLICATION_ID', system_helper_application_id)
system_helper_config.set_quoted('SESSION_HELPER_APPLICATION_ID', session_helper_application_id)
system_helper_config.set_quoted('LIBEXECDIR', libexecdir)

config_file = configure_file(
    output: 'config.h',
    configuration: system_helper_config
)

common_dependencies = [
    gio_dep,
    gio_unix_dep,
    glib_dep,
    gobject_dep
]

eos_kolibri_dbus_lib = static_library(
    'eos_kolibri_dbus',
    sources: gnome.gdbus_codegen(
        'eos-kolibri-dbus',
        'org.endlessos.Kolibri.xml',
        interface_prefix: 'org.endlessos.',
        namespace: 'EosKolibriDBus',
        object_manager: true,
    ),
    dependencies: common_dependencies,
    include_directories: include_directories('.')
)

eos_kolibri_dbus_lib_dep = declare_dependency(
    link_with: eos_kolibri_dbus_lib,
    dependencies: common_dependencies,
    include_directories: include_directories('.')
)

eos_kolibri_dependencies = [
    common_dependencies,
    eos_kolibri_dbus_lib_dep
]

executable(
    'kolibri-system-helper',
    sources: [
        'eos-kolibri-system-helper.c',
        'eos-kolibri-system-helper-main.c'
    ],
    dependencies: eos_kolibri_dependencies,
    install: true,
    install_dir: libexecdir
)

executable(
    'kolibri-session-helper',
    sources: [
        'eos-kolibri-session-helper.c',
        'eos-kolibri-session-helper-main.c',
        'eos-kolibri-share-directory-context.c'
    ],
    dependencies: eos_kolibri_dependencies,
    install: true,
    install_dir: libexecdir
)

