from gi import require_versions as gi_required
gi_required({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Adw, Gio

from gettext import gettext as _

from suraimu import config

@Gtk.Template(resource_path=f"{config.RESOURCES}/preferences-window.ui")
class PreferencesWindow(Adw.PreferencesWindow):

    __gtype_name__ = "PreferencesWindow"

    animations_row: Adw.ExpanderRow = Gtk.Template.Child()
    animations_preload_switch: Gtk.Switch = Gtk.Template.Child()

    settings = Gio.Settings.new(config.APP_ID)

    def __init__(self, **kwargs):
        super().__init__()

        self.app = kwargs.get("application")

        self.settings.bind("animations", self.animations_row, "enable-expansion", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("animations-preload", self.animations_preload_switch, "active", Gio.SettingsBindFlags.DEFAULT)
