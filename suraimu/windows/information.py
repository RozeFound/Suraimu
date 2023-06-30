from gi import require_versions as gi_required
gi_required({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Adw, Gdk

from gettext import gettext as _

from suraimu import config
from suraimu.backend.steam import WallpaperEntry, Steam
from suraimu.windows.properties import PropertiesWindow

@Gtk.Template(resource_path=f"{config.RESOURCES}/info-window.ui")
class InfoWindow(Adw.Window):

    __gtype_name__ = 'InfoWindow'

    preferences_button: Gtk.Button = Gtk.Template.Child()
    preview: Gtk.Picture = Gtk.Template.Child()

    id_property: Adw.ActionRow = Gtk.Template.Child()
    type_property: Adw.ActionRow = Gtk.Template.Child()
    rating_property: Adw.ActionRow = Gtk.Template.Child()
    tags_property: Adw.ActionRow = Gtk.Template.Child()

    description_property_group: Adw.PreferencesGroup = Gtk.Template.Child()
    description_property: Adw.ActionRow = Gtk.Template.Child()

    def __init__(self, paintable: Gdk.Paintable, info: WallpaperEntry) -> None:
        super().__init__()

        if paintable: self.preview.set_paintable(paintable)
        else: self.preview.set_visible(False)
        self.set_title(info.title)
        self.info = info

        if not info.has_properties: self.preferences_button.set_visible(False)

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

        if not hasattr(self, "properties_window"):
            self.properties_window = PropertiesWindow(self.info)

        self.properties_window.set_transient_for(self)
        self.properties_window.present()

    @Gtk.Template.Callback()
    def on_folder_button_clicked(self, *args) -> None:
        uri = f"file://{self.info.path}"
        Gtk.show_uri(self, uri, Gdk.CURRENT_TIME)

    @Gtk.Template.Callback()
    def on_apply_button_clicked(self, *args) -> None:
        print("on_apply_button_clicked", self.info.title, "info_window")


