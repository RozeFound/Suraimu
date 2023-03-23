pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
widgetsdir = join_paths(pkgdatadir, 'suraimu/widgets')

suraimu_sources = [
  '__init__.py',
  'theme_switcher.py',
  'library.py'
]

install_data(suraimu_sources, install_dir: widgetsdir)