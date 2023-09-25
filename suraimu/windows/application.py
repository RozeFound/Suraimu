from gi import require_versions as gi_required
gi_required({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Adw, Gio

from gettext import gettext as _

from suraimu import config
from suraimu.views.not_implemented import NotImplemented
from suraimu.views.library import Library
from suraimu.widgets.theme_switcher import ThemeSwitcher

@Gtk.Template(resource_path=f"{config.RESOURCES}/window.ui")
class MainWindow(Adw.ApplicationWindow):

    __gtype_name__ = 'MainWindow'

    options_menu: Gtk.PopoverMenu = Gtk.Template.Child()
    stack: Adw.ViewStack = Gtk.Template.Child()

    settings = Gio.Settings.new(config.APP_ID)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings.bind("width", self, "default_width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("height", self, "default_height", Gio.SettingsBindFlags.DEFAULT)

        self.app = kwargs.get("application")

        if config.BUILD_TYPE == "dev":
            self.add_css_class("devel")

        self.theme_switcher = ThemeSwitcher()
        self.options_menu.add_child(self.theme_switcher, "theme")

        self.populate_stack()

    def populate_stack(self) -> None:

        self.page_installed = Library()
        self.page_browse = NotImplemented()
        self.page_workshop = NotImplemented()

        self.stack.add_titled_with_icon(self.page_installed, 
        "page_installed", _("Installed"), "folder-symbolic")
        self.stack.add_titled_with_icon(self.page_browse, 
            "page_browse", _("Browse"), "web-browser-symbolic")
        self.stack.add_titled_with_icon(self.page_workshop, 
            "page_workshop", _("Workshop"), "people-symbolic")
        

