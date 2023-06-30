from gi import require_versions as gi_required
gi_required({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Adw

from gettext import gettext as _

from suraimu import config

@Gtk.Template(resource_path=f"{config.RESOURCES}/preferences-window.ui")
class PreferencesWindow(Adw.PreferencesWindow):

    __gtype_name__ = "PreferencesWindow"

    def __init__(self, **kwargs):
        super().__init__()

        self.app = kwargs.get("application")

