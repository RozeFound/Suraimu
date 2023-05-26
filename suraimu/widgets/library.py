import gi

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk
from suraimu import config
from suraimu.backend.steam import WallpaperEntry

@Gtk.Template(resource_path=f"{config.RESOURCES}/library-entry.ui")
class LibraryEntry(Gtk.Box):

    __gtype_name__ = "LibraryEntry"

    overlay: Gtk.Overlay = Gtk.Template.Child()
    no_preview_label: Gtk.Label = Gtk.Template.Child()
    preview: Gtk.Picture = Gtk.Template.Child()
    revealer: Gtk.Revealer = Gtk.Template.Child()
    label: Gtk.Label = Gtk.Template.Child()
    info_button: Gtk.Button = Gtk.Template.Child()

    def __init__(self, wallpaper: WallpaperEntry, **kwargs) -> None:
        super().__init__(**kwargs)

        self.wallpaper = wallpaper
        self.label.set_text(wallpaper.title)

        if wallpaper.preview: 
            # Gtk.Picture.set_pixbuf deprecated in GTK 4.12
            self.preview.set_filename(wallpaper.preview.as_posix())
            self.preview.set_visible(True)
            self.no_preview_label.set_visible(False)

        motion_controller = Gtk.EventControllerMotion.new()
        motion_controller.connect("enter", self.on_motion_enter)
        motion_controller.connect("leave", self.on_motion_leave)
        self.overlay.add_controller(motion_controller)

    def on_motion_enter(self, *args) -> None:
        self.revealer.set_reveal_child(True)

    def on_motion_leave(self, *args) -> None:
        self.revealer.set_reveal_child(False)

    @Gtk.Template.Callback()
    def on_info_button_clicked(self, *args) -> None:
        print(self.wallpaper.title, "info button clicked")
