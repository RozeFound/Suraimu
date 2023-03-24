import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, GObject
from gettext import gettext as _

from suraimu.widgets.library import LibraryEntry
from suraimu.backend.steam import Steam
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

        if (status := self.steam.get_status()) != "OK":        
            match status:
                case "STEAM NOT FOUND": self.placeholder.set_title(_("No Steam installations found."))
                case "WORKSHOP NOT ACCESIBLE": 
                    self.placeholder.set_title(_("Failed to find workshop items"))
                    self.placeholder.set_description(_("You likely use external steam library, and didn't set the permission to access it."))
        else: GLib.idle_add(self.fill_flow_grid)

    def fill_flow_grid(self) -> None: 

        item_ids = self.steam.list_workshop_items()
        items = [self.steam.get_wallpaper(id) for id in item_ids]

        for item in items: 
            self.items_per_line += 1
            entry = LibraryEntry(item)
            self.flow.append(entry)

        self.placeholder.set_visible(False)
        self.scroll.set_visible(True)

        
