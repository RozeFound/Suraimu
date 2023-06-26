import gi

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gdk, GObject
from pathlib import Path

from suraimu import config
from suraimu.backend.steam import WallpaperEntry
from suraimu.windows.information import InfoWindow
from suraimu.widgets.animation import Animation
from suraimu.backend.utils import Async

@Gtk.Template(resource_path=f"{config.RESOURCES}/library-entry.ui")
class LibraryEntry(Gtk.Box):

    __gtype_name__ = "LibraryEntry"

    overlay: Gtk.Overlay = Gtk.Template.Child()
    no_preview_label: Gtk.Label = Gtk.Template.Child()

    preview: Gtk.Picture = Gtk.Template.Child()
    paintable = GObject.Property(type=Gdk.Paintable)

    revealer: Gtk.Revealer = Gtk.Template.Child()
    label: Gtk.Label = Gtk.Template.Child()
    info_button: Gtk.Button = Gtk.Template.Child()

    initialized = False

    def __init__(self, wallpaper: WallpaperEntry, **kwargs) -> None:
        super().__init__(**kwargs)

        self.wallpaper = wallpaper
        self.label.set_text(wallpaper.title)

        if wallpaper.preview: self.load_preview(wallpaper.preview)

        motion_controller = Gtk.EventControllerMotion.new()
        motion_controller.connect("enter", self.on_motion_enter)
        motion_controller.connect("leave", self.on_motion_leave)
        self.overlay.add_controller(motion_controller)
        
    @Async.function
    def load_preview(self, preview_path: Path) -> None:  

        if (preview_path.suffix == ".gif"): self.paintable = Animation(preview_path)
        else: self.paintable = Gdk.Texture.new_from_filename(preview_path.as_posix())
            
        self.preview.set_visible(True)
        self.no_preview_label.set_visible(False)
        self.initialized = True

    def on_motion_enter(self, *args) -> None:
        self.revealer.set_reveal_child(True)

    def on_motion_leave(self, *args) -> None:
        self.revealer.set_reveal_child(False)

    @Gtk.Template.Callback()
    def on_info_button_clicked(self, *args) -> None:

        info_window = InfoWindow(self.paintable, self.wallpaper)
        info_window.set_transient_for()
        info_window.present()