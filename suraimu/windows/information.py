import gi, re

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gdk
from gettext import gettext as _

from suraimu import config
from suraimu.backend.steam import WallpaperEntry, Steam, Property

HTML_REGEX = re.compile('<.*?>')

def get_property_row(property: Property) -> Adw.ActionRow | Adw.ComboRow | Adw.EntryRow:

    if property.title != "ui_browse_properties_scheme_color": 
        title = re.sub(HTML_REGEX, '', property.title) 
    else: title = _("Scheme Color") 

    row = Adw.ActionRow(title=title, use_markup=True)

    match property.type:
        case "bool": 
            switch = Gtk.Switch(active=property.value, valign=Gtk.Align.CENTER)
            row.set_activatable_widget(switch)
            row.add_suffix(switch)
        case "color": 
            dialog = Gtk.ColorDialog(title=_("Choose color"), with_alpha=False)
            values = [float(x) for x in property.value.split(" ")]
            rgba = Gdk.RGBA(); rgba.alpha = 1.0
            rgba.red, rgba.green, rgba.blue = values            
            button = Gtk.ColorDialogButton(rgba=rgba, dialog=dialog, valign=Gtk.Align.CENTER)
            row.set_activatable_widget(button)
            row.add_suffix(button)
        case "slider":
            slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,
                               adjustment=Gtk.Adjustment(value=float(property.value),
                               lower=property.min, upper=property.max, step_increment=property.step),
                               hexpand=True, valign=True, draw_value=True, value_pos=Gtk.PositionType.LEFT)
            row.set_activatable_widget(slider)
            row.add_suffix(slider)
        case "combo":
            row = Adw.ComboRow(title=title, use_markup=True)
            string = list(property.options.keys())
            string_list = Gtk.StringList(strings=string)
            row.set_model(string_list)
        case "textinput": row = Adw.EntryRow(title=title, text=property.value, use_markup=True)

    return row

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

        window = Adw.PreferencesWindow(title=_("Wallpaper Properties"))
        page = Adw.PreferencesPage(); window.add(page)
        group = Adw.PreferencesGroup(); page.add(group)

        properties = Steam.get_properties_for_wallpaper(self.info)

        for property in properties:
            group.add(get_property_row(property))

        window.set_transient_for(self)
        window.present()

    @Gtk.Template.Callback()
    def on_folder_button_clicked(self, *args) -> None:
        uri = f"file://{self.info.path}"
        Gtk.show_uri(self, uri, Gdk.CURRENT_TIME)

    @Gtk.Template.Callback()
    def on_apply_button_clicked(self, *args) -> None:
        print("on_apply_button_clicked", self.info.title, "info_window")


