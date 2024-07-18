project('suraimu', 'rust',
          version: '0.0.0-dev',
    meson_version: '>= 0.59.0',
  default_options: [ 'warning_level=2' ],
)

APP_NAME = 'Suraimu'
APP_VERSION = meson.project_version()

APPLICATION_ID = 'com.github.RozeFound.Suraimu'
PKGDATA_DIR = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

dependency('glib-2.0', version: '>= 2.76') # update when changing gtk version
dependency('gio-2.0', version: '>= 2.76') # always same version as glib
dependency('gtk4', version: '>= 4.12.0')
dependency(
  'libadwaita-1', version: '>= 1.5',
  fallback: ['libadwaita', 'libadwaita_dep'],
  default_options: ['tests=false', 'examples=false', 'vapi=false']
)

cargo = find_program('cargo', required: true)
cargo_version = run_command(cargo, '--version', check: true).stdout().strip()
message(cargo_version)
rustc_version = run_command('rustc', '--version', check: true).stdout().strip()
message(rustc_version)

i18n = import('i18n')
gnome = import('gnome')
localedir = get_option('localedir')

subdir('data')
subdir('po')
subdir('src')

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)