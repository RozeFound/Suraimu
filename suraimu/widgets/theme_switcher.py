from gi import require_versions as gi_required
gi_required({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Adw, Gio, GObject

from suraimu import config

@Gtk.Template(resource_path=f"{config.RESOURCES}/theme-switcher.ui")
class ThemeSwitcher(Gtk.Box):

    __gtype_name__ = "ThemeSwitcher"

    system: Gtk.CheckButton = Gtk.Template.Child()
    light: Gtk.CheckButton = Gtk.Template.Child()
    dark: Gtk.CheckButton = Gtk.Template.Child()

    settings = Gio.Settings.new(config.APP_ID)

    color_scheme = GObject.property(type=int, default=Adw.ColorScheme.DEFAULT)
    show_system = GObject.property(type=bool, default=True)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.settings.bind("color-scheme", self, "color-scheme", Gio.SettingsBindFlags.DEFAULT)

        self.style_manager = Adw.StyleManager.get_default()
        self.style_manager.bind_property("system-supports-color-schemes",self, "show-system", GObject.BindingFlags.SYNC_CREATE)
        self.style_manager.bind_property("color-scheme", self, "color-scheme", GObject.BindingFlags.BIDIRECTIONAL)

        match self.color_scheme:
            case Adw.ColorScheme.DEFAULT: self.system.activate()
            case Adw.ColorScheme.FORCE_LIGHT: self.light.activate()
            case Adw.ColorScheme.FORCE_DARK: self.dark.activate()

    @Gtk.Template.Callback()
    def on_color_scheme_changed(self, *args) -> None:
        if self.system.get_active(): self.color_scheme = 0
        elif self.light.get_active(): self.color_scheme = 1
        elif self.dark.get_active(): self.color_scheme = 4