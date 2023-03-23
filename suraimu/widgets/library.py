import gi

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GLib
from gi.repository.GdkPixbuf import Pixbuf
from suraimu import config
from suraimu.backend.steam import WallpaperEntry

@Gtk.Template(resource_path=f"{config.RESOURCES}/library-entry.ui")
class LibraryEntry(Gtk.Box):

    __gtype_name__ = "LibraryEntry"

    overlay: Gtk.Overlay = Gtk.Template.Child()
    no_preview_label: Gtk.Label = Gtk.Template.Child()
    preview: Gtk.Picture = Gtk.Template.Child()

    def __init__(self, wallpaper: WallpaperEntry, **kwargs) -> None:
        super().__init__(**kwargs)

        self.wallpaper = wallpaper

        if wallpaper.preview:
            try: pixbuf = Pixbuf.new_from_file(
                    wallpaper.preview.as_posix())
            except GLib.Error: pixbuf = None
            if pixbuf:
                self.preview.set_pixbuf(pixbuf)
                self.preview.set_visible(True)
                self.no_preview_label.set_visible(False)

        motion_controller = Gtk.EventControllerMotion.new()
        motion_controller.connect("enter", self.on_motion_enter)
        motion_controller.connect("leave", self.on_motion_leave)
        self.overlay.add_controller(motion_controller)

    def on_motion_enter(self, *args) -> None:
        print(f"on_motion_enter: {self.wallpaper.title}")

    def on_motion_leave(self, *args) -> None:
        print(f"on_motion_leave: {self.wallpaper.title}")
