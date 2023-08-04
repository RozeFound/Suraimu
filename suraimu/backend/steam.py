from pathlib import Path
from typing import Any
from vdf import loads as parse_vdf
from json import loads as parse_json
from json import dumps as write_json
from dataclasses import dataclass
import os

@dataclass
class WallpaperEntry:

    id: str
    type: str
    official: bool

    title: str
    rating: str
    description: str | None

    preview: Path | None
    tags: list[str] | None
    path: Path

@dataclass
class Property:

    id: str
    title: str
    index: int

    condition: str | None
    options: dict | None

    min: int
    max: int
    step: int

    fraction: bool
    precision: int

    type: str
    default: Any
    value: Any

class Steam:

    STEAM_APP_ID = 431960

    def __init__(self) -> None:

        self.status = "OK"

        if not (path := self.get_steam_path()):
            self.status = "STEAM NOT FOUND"; return
        else: self.steam_path = path

        if not (path := self.get_library_path()):
            self.status = "LIBRARY NOT FOUND"; return
        else: self.library_path = path

        if not (path := self.get_official_projects_directory()):
            self.status = "APP NOT FOUND"; return
        else: self.projects_path = path

        if not (path := self.get_workshop_directory()):
            self.status = "WORKSHOP NOT ACCESIBLE"; return
        else: self.workshop_path = path

    def get_status(self) -> str:
        return self.status

    def get_steam_path(self) -> Path | None:

        available_locations = (".steam/steam", ".var/app/com.valvesoftware.Steam/.steam/steam")

        for location in available_locations:
            path = Path().home() / location
            if path.exists(): return path

    def get_library_path(self) -> Path | None:

        libraries_cfg = self.steam_path / "config/libraryfolders.vdf"
        if not libraries_cfg.exists(): return
        libraries: dict = parse_vdf(libraries_cfg.read_text())

        for library in libraries.get("libraryfolders", {}).values():
            if str(self.STEAM_APP_ID) in library.get("apps", {}).keys():
               path = Path(library.get("path"))
               if path.exists(): return path

    def get_workshop_directory(self) -> Path | None:
        path = self.library_path / f"steamapps/workshop/content/{self.STEAM_APP_ID}"
        if path.exists(): return path

    def get_official_projects_directory(self) -> Path | None:
        path = self.library_path / "steamapps/common/wallpaper_engine/projects/defaultprojects"
        if path.exists(): return path

    @staticmethod
    def get_locale(locale: str) -> dict:

        instance = Steam()
        locale_dir = instance.library_path / "steamapps/common/wallpaper_engine/locale"

        file = locale_dir / f"ui_{locale}.json"
        if file.exists(): 
            data = file.read_text()
            return parse_json(data)
        else: 
            return instance.get_locale("en-us")

    def list_workshop_items(self) -> list[int]:
        return [int(id.name) for id in self.workshop_path.iterdir()]

    def list_official_projects(self) -> list[str]:
        return [id.name for id in self.projects_path.iterdir()]

    def get_wallpapers(self) -> list[WallpaperEntry]: 
        ids = self.list_workshop_items() + self.list_official_projects()
        result = [self.get_wallpaper(id) for id in ids]
        return [entry for entry in result if entry]

    def get_wallpaper(self, id: int | str) -> WallpaperEntry | None:

        for root in (self.workshop_path, self.projects_path):
            path = root / str(id) 
            project = path / "project.json"
            if project.exists(): break
        else: return

        json = parse_json(project.read_text())
        preview = path / json.get("preview", "unknown")

        if category := json.get("category"):
            if category == "Asset": return

        return WallpaperEntry(
            id=str(id),
            official=json.get("official", False),
            # TODO: Implement Presets, for not it's just for identification
            type=json.get("type", "Preset" if "preset" in json else None),
            title=json.get("title", "unknown"),
            rating=json.get("contentrating", "Everyone"),
            description=json.get("description"),
            preview=preview if preview.exists() else None,
            tags=json.get("tags"),
            path=path
        )

class Properties:

    xdg_data_home = os.environ.get("XDG_DATA_HOME", os.path.join(Path.home(), ".local/share"))
    properties_dir = Path(xdg_data_home) / "suraimu" / "changed_properties"

    @staticmethod
    def get(wallpaper: WallpaperEntry) -> dict[str, Property]:

        project = wallpaper.path / "project.json"
        json = parse_json(project.read_text())
        properties: dict[str, Property] = dict()

        changed_properties = Properties.properties_dir / f"{wallpaper.id}.json"
        if changed_properties.exists(): 
            changed_properties_json = parse_json(changed_properties.read_text())
        else: changed_properties_json = {}

        for key, value in json.get("general", {}).get("properties", {}).items():

            title = value.get("name", value.get("text"))

            if(options := value.get("options")):
                options = { option.get("label"): option.get("value") for option in options }

            default = value.get("value")
            if value.get("type") == "slider" and isinstance(default, str): 
                if default.isdigit(): default = int(default)
                else: default = float(default)

            properties[key] = Property(
                id=key,
                title=title,

                index=value.get("index", value.get("order", 0)),
                condition=value.get("condition"),
                options=options,

                min=value.get("min"),
                max=value.get("max"),
                step=value.get("step", 1),

                fraction=value.get("fraction", False),
                precision=value.get("precision", 1),
                
                type=value.get("type"),

                default=default,
                value=changed_properties_json.get(key, default)
            )

        return properties

    @staticmethod
    def set(wallpaper: WallpaperEntry, property: Property) -> None:

        properties = Properties.properties_dir / f"{wallpaper.id}.json"
        if not properties.parent.exists(): properties.parent.mkdir(parents=True)
        
        if properties.exists(): 
            json = parse_json(properties.read_text())
        else: json = {}

        if property.value == property.default:
            if property.id in json: del json[property.id]
        else: json[property.id] = property.value

        if not json:
            if properties.exists():
                properties.unlink()
            return

        properties.write_text(write_json(json, indent=4))
    