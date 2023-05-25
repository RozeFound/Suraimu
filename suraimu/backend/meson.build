pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
backenddir = join_paths(pkgdatadir, 'suraimu/backend')

suraimu_sources = [
  '__init__.py',
  'steam.py',
  'utils.py',
]

install_data(suraimu_sources, install_dir: backenddir)