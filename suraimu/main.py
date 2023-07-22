from gi import require_versions as gi_required
gi_required({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Adw, Gio

from typing import Callable

from suraimu.windows.application import MainWindow
from suraimu.windows.preferences import PreferencesWindow
from suraimu import config

class Suraimu(Adw.Application):

    def __init__(self, version: str) -> None:
        super().__init__(application_id=config.APP_ID, register_session=True)
        self.set_resource_base_path(config.RESOURCES)
        print(f"Initializing Suraimu v{version}")

        self.create_action("about", self.show_about)
        self.create_action("preferences", self.show_preferences, ["<primary>comma"])
        self.create_action("exit", self.exit, ["<primary>q"])

    def create_action(self, name: str, callback: Callable, shortcuts: list[str] = None) -> None:

        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)

        if shortcuts: self.set_accels_for_action(f"app.{name}", shortcuts)

    def show_preferences(self, *args) -> None:

        preferences = PreferencesWindow(application=self)
        preferences.set_transient_for(self.window)
        preferences.present()

    def show_about(self, *args) -> None:
        
        builder = Gtk.Builder.new_from_resource(f"{config.RESOURCES}/about.ui")

        about = builder.get_object("about_window")
        about.set_application_name(config.APP_NAME)
        about.set_application_icon(config.APP_ICON)
        about.set_version(config.APP_VERSION)

        about.set_transient_for(self.window)
        about.present()

    def do_activate(self) -> None:

        Adw.Application.do_activate(self)
        window = self.props.active_window
        if not window: window = MainWindow(application=self)
        self.window = window
        window.present()

    def exit(self, *args) -> None:
        self.window.on_close_request()
        print("Closing Suraimu...")
        quit(0)

def main(version: str, argv: list[str]) -> int:

    if config.BUILD_TYPE == "dev":
        from debugpy import listen
        listen(("localhost", 5678))

    app = Suraimu(version)
    return app.run(argv)

