from gi.repository import GObject, Gdk, Gtk, GLib, Gio, GdkPixbuf, Graphene

from suraimu import config
import imageio.v3 as iio
from numpy import ndarray
from pathlib import Path

def create_texture(image: ndarray) -> Gdk.Texture:
        
    pixbuf = GdkPixbuf.Pixbuf.new_from_data(
        image.tobytes(), 
        GdkPixbuf.Colorspace.RGB,
        False,
        8,
        image.shape[1],
        image.shape[0],
        image.shape[1] * image.shape[2]
    )

    return Gdk.Texture.new_for_pixbuf(pixbuf)

class Animation(GObject.GObject, Gdk.Paintable):

    __gtype_name__ = "GifAnimation"

    settings = Gio.Settings.new(config.APP_ID)

    enabled = settings.get_boolean("animations")
    preload = settings.get_boolean("animations-preload")

    def __init__(self, path: Path, autoplay = True) -> None:

        super().__init__()

        self.settings.connect("changed::animations", lambda *args: (
            enabled := self.settings.get_boolean("animations"),
            self.play() if enabled else self.pause()))

        props = iio.improps(path, plugin="pyav")
        self.height, self.width = props.shape[1], props.shape[2]
        self.n_images = props.n_images

        meta = iio.immeta(path, plugin="pyav")
        self.interval = 1000 // meta.get("fps")

        self.iter = iio.imiter(path, plugin="pyav")
        self.textures: list[Gdk.Texture] = list()

        if self.preload and self.enabled:
            self.textures = [create_texture(image) for image in self.iter]
        else: self.textures = [create_texture(next(self.iter))] # we preload the first frame anyway

        self.playing = False
        self.current_frame = 0
        if autoplay and self.enabled: self.play()

    def do_get_intrinsic_width(self) -> int: return self.width
    def do_get_intrinsic_height(self) -> int: return self.height
    def do_get_intrinsic_aspect_ratio(self) -> float: return self.width / self.height
    def do_get_flags(self) -> Gdk.PaintableFlags: return Gdk.PaintableFlags(Gdk.PaintableFlags.SIZE)

    def do_get_current_image(self) -> Gdk.Paintable: 

        if len(self.textures) <= self.current_frame:
            image = next(self.iter)
            texture = create_texture(image)
            self.textures.append(texture)
        else: texture = self.textures[self.current_frame]

        return texture

    def do_snapshot(self, snapshot: Gtk.Snapshot, width: float, height: float) -> None:

        texture = self.get_current_image()

        rect = Graphene.Rect()
        rect = rect.init(0, 0, width, height)
        snapshot.append_texture(texture, rect)

    def invalidate_contents(self) -> bool:

        super().invalidate_contents()
        self.current_frame = (self.current_frame + 1) % self.n_images
        return GLib.SOURCE_CONTINUE if self.playing else GLib.SOURCE_REMOVE
        
    def play(self) -> None:
        self.playing = True
        GLib.timeout_add(self.interval, self.invalidate_contents)

    def pause(self) -> None:
        self.playing = False