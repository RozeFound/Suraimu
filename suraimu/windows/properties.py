from gi import require_versions as gi_required
gi_required({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Adw, Gdk

from gettext import gettext as _
from re import compile as re_compile
from locale import getlocale
from suraimu.backend.steam import Properties, WallpaperEntry, Property, Steam

class PropertiesWindow(Adw.PreferencesWindow):

    __gtype_name__ = "PropertiesWindow"

    def __init__(self, info: WallpaperEntry, **kwargs):

        super().__init__(title=_("Wallpaper Properties"), **kwargs)

        self.page = Adw.PreferencesPage(); self.add(self.page)
        self.group = Adw.PreferencesGroup(); self.page.add(self.group)
        self.conditions: list[tuple[str, Adw.ActionRow | Adw.ComboRow | Adw.EntryRow]] = list() 

        self.info = info
        self.html_tag_regex = re_compile('<.*?>')
        self.condition_regex = re_compile(r"(?P<key>\w+?)\.\w+?\b")

        self.properties = Properties.get(info)
        locale_code = getlocale()[0].lower().replace('_', '-')
        self.locale = Steam.get_locale(locale_code)

        self.fill_properties_and_conditions()
        self.change_visibility_if_necessary()

    def fill_properties_and_conditions(self) -> None:

        for property in sorted(self.properties.values(), key=lambda x: x.index):

            title = self.locale.get(property.title, self.html_tag_regex.sub('', property.title))

            match property.type:
                case "bool": get_property_row = self.add_bool_property
                case "color": get_property_row = self.add_color_property
                case "slider": get_property_row = self.add_slider_property
                case "combo": get_property_row = self.add_combo_property
                case "textinput": get_property_row = self.add_textinput_property

            row = get_property_row(title, property)
            self.group.add(row)

            if condition := property.condition:

                match = self.condition_regex.findall(condition)
                for key in match: condition = condition.replace(key, f"self.properties['{key}']")

                condition = condition.replace("&&", "and").replace("||", "or")
                condition = condition.replace("false", "False").replace("true", "True")

                self.conditions.append((condition, row))

    def change_visibility_if_necessary(self) -> None:
        for condition, row in self.conditions: 
            if condition: row.set_visible(eval(condition))

    def on_value_changed(self, widget: Gtk.Widget, *args) -> None:

        property = [x for x in args if isinstance(x, Property)][0]

        if isinstance(widget, Gtk.Switch):
            property.value = widget.get_active()
            self.change_visibility_if_necessary()
        if isinstance(widget, Gtk.Scale):
            property.value = widget.get_value()
            self.change_visibility_if_necessary()
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

    def add_bool_property(self, title: str, property: Property) -> Adw.ActionRow:

        switch = Gtk.Switch(active=property.value, valign=Gtk.Align.CENTER)
        switch.connect("state-set", self.on_value_changed, property)

        row = Adw.ActionRow(title=title, activatable_widget=switch)
        row.add_suffix(switch)

        return row

    def add_color_property(self, title: str, property: Property) -> Adw.ActionRow:

        dialog = Gtk.ColorDialog(title=_("Choose color"), with_alpha=False)

        values = [float(x) for x in property.value.split(" ")]
        rgba = Gdk.RGBA(); rgba.alpha = 1.0
        rgba.red, rgba.green, rgba.blue = values  

        button = Gtk.ColorDialogButton(rgba=rgba, dialog=dialog, valign=Gtk.Align.CENTER)
        button.connect("notify::rgba", self.on_value_changed, property)

        row = Adw.ActionRow(title=title, activatable_widget=button)
        row.add_suffix(button)

        return row

    def add_slider_property(self, title: str, property: Property) -> Adw.ActionRow:

        slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,
                           adjustment=Gtk.Adjustment(value=property.value, 
                           lower=property.min, upper=property.max,
                           step_increment=property.step, page_increment=property.step),
                           digits=property.precision if property.fraction else 0,
                           hexpand=True, valign=True, draw_value=True, value_pos=Gtk.PositionType.LEFT)                   
        slider.connect("value-changed", self.on_value_changed, property)

        row = Adw.ActionRow(title=title, activatable_widget=slider)
        row.add_suffix(slider)

        return row

    def add_combo_property(self, title: str, property: Property) -> Adw.ComboRow:

        strings = [self.locale.get(key, key) for key in property.options.keys()]
        string_list = Gtk.StringList(strings=strings)

        selected = 0
        
        for i, value in enumerate(property.options.values()):
            if property.value == value: selected = i

        row = Adw.ComboRow(title=title, model=string_list, selected=selected)
        row.connect("notify::selected", self.on_value_changed, property)

        return row

    def add_textinput_property(self, title: str, property: Property) -> Adw.EntryRow:

        row = Adw.EntryRow(title=title, text=property.value)
        row.connect("changed", self.on_value_changed, property)

        return row
