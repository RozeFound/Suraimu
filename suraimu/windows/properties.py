from gi import require_versions as gi_required
gi_required({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Adw, Gdk

from gettext import gettext as _
from re import compile as re_compile
from suraimu.backend.steam import Properties, WallpaperEntry, Property

class PropertiesWindow(Adw.PreferencesWindow):

    __gtype_name__ = "PropertiesWindow"

    def __init__(self, info: WallpaperEntry, **kwargs):

        super().__init__(title=_("Wallpaper Properties"), **kwargs)

        self.page = Adw.PreferencesPage(); self.add(self.page)
        self.group = Adw.PreferencesGroup(); self.page.add(self.group)
        self.items: list[tuple[Property, Adw.ActionRow]] = list() 

        self.info = info
        self.html_tag_regex = re_compile('<.*?>')
        self.condition_regex = re_compile(r"(?P<key>\w+?)\.\w+?\b")

        self.properties = Properties.get(info)
    
        for property in sorted(self.properties.values(), key=lambda x: x.order):

            title = self.html_tag_regex.sub('', property.title) 

            if property.condition:

                match = self.condition_regex.findall(property.condition)

                for key in match: property.condition = property.condition.replace(key, f"self.properties['{key}']")

                property.condition = property.condition.replace("&&", "and").replace("||", "or")
                property.condition = property.condition.replace("false", "False").replace("true", "True")

            match property.type:
                case "bool": self.add_bool_property(title, property)
                case "color": self.add_color_property(title, property)
                case "slider": self.add_slider_property(title, property)
                case "combo": self.add_combo_property(title, property)
                case "textinput": self.add_textinput_property(title, property)

        self.change_visibility_if_necessary()

    def change_visibility_if_necessary(self) -> None:
        for property, row in self.items: 
            if  property.condition:
                row.set_visible(eval(property.condition))

    def on_value_changed(self, widget: Gtk.Widget, *args) -> None:

        property = [x for x in args if isinstance(x, Property)][0]

        value = None

        if isinstance(widget, Gtk.Switch):
            property.value = widget.get_active()
            self.change_visibility_if_necessary()
        if isinstance(widget, Gtk.Scale):
            property.value = widget.get_value()
        if isinstance(widget, Gtk.ColorDialogButton):
            rgba = widget.get_rgba()
            rgb = [rgba.red, rgba.green, rgba.blue]
            property.value = " ".join([str(x) for x in rgb])
        if isinstance(widget, Adw.ComboRow):
            index = widget.get_selected()
            values = list(property.options.values())
            property.value = values[index]
        if isinstance(widget, Adw.EntryRow):
            property.value = widget.get_text()

        Properties.set(self.info, property)

    def add_bool_property(self, title: str, property: Property):

        switch = Gtk.Switch(active=property.value, valign=Gtk.Align.CENTER)
        switch.connect("state-set", self.on_value_changed, property)

        row = Adw.ActionRow(title=title, activatable_widget=switch)
        row.add_suffix(switch)

        self.group.add(row); self.items.append((property, row))

    def add_color_property(self, title: str, property: Property):

        if property.title == "ui_browse_properties_scheme_color": title = _("Scheme Color") 
        dialog = Gtk.ColorDialog(title=_("Choose color"), with_alpha=False)

        values = [float(x) for x in property.value.split(" ")]
        rgba = Gdk.RGBA(); rgba.alpha = 1.0
        rgba.red, rgba.green, rgba.blue = values  

        button = Gtk.ColorDialogButton(rgba=rgba, dialog=dialog, valign=Gtk.Align.CENTER)
        button.connect("notify::rgba", self.on_value_changed, property)
        row = Adw.ActionRow(title=title, activatable_widget=button)
        row.add_suffix(button)

        self.group.add(row); self.items.append((property, row))

    def add_slider_property(self, title: str, property: Property):

        slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,
                           adjustment=Gtk.Adjustment(value=float(property.value),
                           lower=property.min, upper=property.max, step_increment=property.step),
                           hexpand=True, valign=True, draw_value=True, value_pos=Gtk.PositionType.LEFT)
        slider.connect("value-changed", self.on_value_changed, property)
        row = Adw.ActionRow(title=title, activatable_widget=slider)
        row.add_suffix(slider)

        self.group.add(row); self.items.append((property, row))

    def add_combo_property(self, title: str, property: Property):

        strings = list(property.options.keys())
        string_list = Gtk.StringList(strings=strings)
        row = Adw.ComboRow(title=title, model=string_list)
        row.connect("notify::selected", self.on_value_changed, property)

        self.group.add(row); self.items.append((property, row))

    def add_textinput_property(self, title: str, property: Property):

        row = Adw.EntryRow(title=title, text=property.value)
        row.connect("changed", self.on_value_changed, property)

        self.group.add(row); self.items.append((property, row))