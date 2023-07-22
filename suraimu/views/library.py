from gi import require_versions as gi_required
gi_required({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Adw, GObject

from gettext import gettext as _
from time import sleep

from suraimu.widgets.library import LibraryEntry
from suraimu.backend.steam import Steam
from suraimu.backend.utils import Async
from suraimu import config

@Gtk.Template(resource_path=f"{config.RESOURCES}/library.ui")
class Library(Adw.Bin):

    __gtype_name__ = "LibraryView"

    placeholder: Adw.StatusPage = Gtk.Template.Child()
    scroll: Gtk.ScrolledWindow = Gtk.Template.Child()
    flow: Gtk.FlowBox = Gtk.Template.Child()

    items_per_line = GObject.property(type=int, default=0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.steam = Steam()

        match self.steam.get_status():
            case "STEAM NOT FOUND": self.placeholder.set_title(_("No Steam installations found."))
            case "LIBRARY NOT FOUND": self.placeholder.set_title(_("Can't find Steam Library."))
            case "APP NOT FOUND": self.placeholder.set_title(_("Can't find Wallpaper Engine."))
            case "WORKSHOP NOT ACCESIBLE": 
                self.placeholder.set_title(_("Failed to find workshop items"))
                self.placeholder.set_description(_("You likely use external steam library, and didn't set the permission to access it."))
            case "OK": self.fill_library()

        self.flow.set_sort_func(self.sort_func)

    def sort_func(self, child_one, child_two):
        left = child_one.get_child().wallpaper.title
        right = child_two.get_child().wallpaper.title
        return -1 if sorted([left, right])[0] == left else 1

    @Async.function
    def fill_library(self) -> None: 

        items = self.steam.get_wallpapers()
        self.items_per_line = len(items)

        for item in items: 
            entry = LibraryEntry(item)
            self.flow.append(entry)
        
        self.placeholder.set_visible(False)
        self.scroll.set_visible(True)