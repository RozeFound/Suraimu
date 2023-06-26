from gi.repository import GObject, Gdk, Gtk, GLib, GdkPixbuf, Graphene

import imageio.v3 as iio
from pathlib import Path

class Animation(GObject.GObject, Gdk.Paintable):

    __gtype_name__ = "GifAnimation"

    paintable: Gdk.Paintable = None

    def __init__(self, path: Path) -> None:

        super().__init__()

        props = iio.improps(path, plugin="pyav")
        self.height, self.width = props.shape[1], props.shape[2]

        meta = iio.immeta(path, plugin="pyav")
        self.delay = 1000 // meta.get("fps")

        self.frames = [frame for frame in iio.imiter(path, plugin="pyav")]

        self.current_frame = 0

        GLib.timeout_add(self.delay, self.play_next_frame) # add this line to start the animation loop

    def do_get_intrinsic_width(self) -> int: return self.width
    def do_get_intrinsic_height(self) -> int: return self.height
    def do_get_current_image(self) -> Gdk.Paintable: return self.paintable

    def do_snapshot(self, snapshot: Gtk.Snapshot, width: float, height: float) -> None:

        frame = self.frames[self.current_frame]

        pixbuf = GdkPixbuf.Pixbuf.new_from_data(
            frame.tobytes(), 
            GdkPixbuf.Colorspace.RGB,
            False,
            8,
            frame.shape[1],
            frame.shape[0],
            frame.shape[1] * frame.shape[2]
        )
        pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)

        rect = Graphene.Rect()
        rect = rect.init(0, 0, width, height)
        snapshot.append_texture(texture, rect)

        self.paintable = texture

    def play_next_frame(self) -> bool:

        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.invalidate_contents()

        return GLib.SOURCE_CONTINUE # return True to continue the loop