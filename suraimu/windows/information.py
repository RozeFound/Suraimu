import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gdk
from gettext import gettext as _

from suraimu import config
from suraimu.backend.steam import WallpaperEntry

@Gtk.Template(resource_path=f"{config.RESOURCES}/info-window.ui")
class InfoWindow(Adw.Window):

    __gtype_name__ = 'InfoWindow'

    preview: Gtk.Picture = Gtk.Template.Child()

    id_property: Adw.ActionRow = Gtk.Template.Child()
    type_property: Adw.ActionRow = Gtk.Template.Child()
    rating_property: Adw.ActionRow = Gtk.Template.Child()
    tags_property: Adw.ActionRow = Gtk.Template.Child()

    description_property_group: Adw.PreferencesGroup = Gtk.Template.Child()
    description_property: Adw.ActionRow = Gtk.Template.Child()

    def __init__(self, image: Gtk.Image, info: WallpaperEntry) -> None:
        super().__init__()

        if image: self.preview.set_paintable(image.get_paintable())
        self.set_title(info.title)
        self.info = info

        if info.id: self.id_property.set_subtitle(str(info.id))
        elif info.official: 
            self.id_property.remove_css_class("property")
            self.id_property.set_title(_("Bundled with Wallpaper Engine"))
        else: self.id_property.set_visible(False)

        if info.type: self.type_property.set_subtitle(info.type.capitalize())
        else: self.type_property.set_visible(False)

        self.rating_property.set_subtitle(info.rating)

        if info.tags: 
            self.tags_property.set_subtitle(",".join(info.tags))
            self.tags_property.set_visible(True)

        if info.description: 
            self.description_property.set_subtitle(info.description)
            self.description_property_group.set_visible(True)

    @Gtk.Template.Callback()
    def on_preferences_button_clicked(self, *args) -> None:
        print("on_preferences_button_clicked", self.info.title, "info_window")

    @Gtk.Template.Callback()
    def on_folder_button_clicked(self, *args) -> None:
        uri = f"file://{self.info.path}"
        Gtk.show_uri(self, uri, Gdk.CURRENT_TIME)

    @Gtk.Template.Callback()
    def on_apply_button_clicked(self, *args) -> None:
        print("on_apply_button_clicked", self.info.title, "info_window")


