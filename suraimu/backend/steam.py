from pathlib import Path
from vdf import loads as parse_vdf
from json import loads as parse_json
from dataclasses import dataclass

@dataclass
class WallpaperEntry:

    id: int
    type: str

    title: str
    rating: str
    description: str

    preview: Path | None
    tags: list[str]

class Steam:

    STEAM_APP_ID = 431960

    def __init__(self) -> None:

        self.status = "OK"

        if not (path := self.get_steam_path()):
            self.status = "STEAM NOT FOUND"
        else: self.steam_path = path

        if self.status != "OK": return

        if not (path := self.get_workshop_directory()):
            self.status = self.status = "WORKSHOP NOT ACCESIBLE"
        else: self.workshop_path = path

    def get_status(self) -> str:
        return self.status

    def get_steam_path(self) -> Path | None:

        available_locations = (".steam/steam", ".var/app/com.valvesoftware.Steam/.steam/steam")

        for location in available_locations:
            path = Path().home() / location
            if path.exists(): return path

    def get_workshop_directory(self) -> Path | None:

        library_path = Path()

        libraries_cfg = self.steam_path / "config/libraryfolders.vdf"
        if not libraries_cfg.exists(): return
        libraries: dict = parse_vdf(libraries_cfg.read_text())

        for library in libraries.get("libraryfolders", {}).values():
            if str(self.STEAM_APP_ID) in library.get("apps", {}).keys():
                library_path = Path(library.get("path"))

        if library_path.exists():
            workshop = library_path / f"steamapps/workshop/content/{self.STEAM_APP_ID}"
            if workshop.exists(): return workshop

    def list_workshop_items(self) -> list[int]:
        return [int(id.name) for id in self.workshop_path.iterdir()]

    def get_wallpaper(self, id: int) -> WallpaperEntry | None:

        path = self.workshop_path / str(id) 
        project = path / "project.json"
        if not project.exists(): return

        json = parse_json(project.read_text())
        preview = path / json.get("preview", "unknown")

        return WallpaperEntry(
            id=json.get("workshopid", 0),
            type=json.get("type", "unknown"),
            title=json.get("title", "unknown"),
            rating=json.get("contentrating", "unknown"),
            description=json.get("description", "No description"),
            preview=preview if preview.exists() else None,
            tags=json.get("tags", [])
        )
