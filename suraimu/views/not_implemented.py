from gi import require_versions as gi_required
gi_required({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Adw

from suraimu import config

@Gtk.Template(resource_path=f"{config.RESOURCES}/placeholder.ui")
class NotImplemented(Adw.Bin):

    __gtype_name__ = "NotImplementedView"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


