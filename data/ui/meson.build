gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    'about.blp',
    'window.blp',
    'placeholder.blp',
    'theme-switcher.blp',
    'library.blp',
    'library-entry.blp',
    'info-window.blp',
    'preferences-window.blp',
    'help_overlay.blp'
    ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'])