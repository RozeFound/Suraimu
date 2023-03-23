pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
windowsdir = join_paths(pkgdatadir, 'suraimu/windows')

suraimu_sources = [
  '__init__.py',
  'main_window.py',
]

install_data(suraimu_sources, install_dir: windowsdir)