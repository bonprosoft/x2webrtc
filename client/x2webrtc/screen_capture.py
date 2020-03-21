import dataclasses
import threading
from typing import Dict, Iterator, List, Optional, Tuple

import Xlib
import Xlib.display
import Xlib.X
from PIL import Image
from Xlib.ext.xtest import fake_input


@dataclasses.dataclass
class Rectangle:
    x: int
    y: int
    width: int
    height: int


class Window:
    def __init__(self, display, screen, window):
        self._display = display
        self._screen = screen
        self._window = window
        self._lock = threading.RLock()

    @property
    def id(self) -> int:
        return self._window.id

    @property
    def wm_name(self) -> Optional[str]:
        with self._lock:
            return self._window.get_wm_name()

    @property
    def wm_class(self) -> Optional[List[str]]:
        with self._lock:
            return self._window.get_wm_class()

    @property
    def owner_id(self) -> int:
        return self._window.owner

    @property
    def rect(self) -> Rectangle:
        with self._lock:
            geo = self._window.get_geometry()
            return Rectangle(geo.x, geo.y, geo.width, geo.height)

    @property
    def properties(self) -> Dict[str, str]:
        with self._lock:
            props = self._window.list_properties()
            atoms = {}
            for p in props:
                atoms[self._display.get_atom_name(p)] = self._window.get_full_text_property(p)

            return atoms

    def get_children(self) -> Iterator["Window"]:
        with self._lock:
            tree = self._window.query_tree()

        for d in tree.children:
            yield Window(self._display, self._screen, d)

    def capture(self, rect: Optional[Rectangle] = None) -> Image.Image:
        with self._lock:
            capture_rect = rect or self.rect
            image = self._window.get_image(
                capture_rect.x, capture_rect.y, capture_rect.width, capture_rect.height, Xlib.X.ZPixmap, 0xFFFFFFFF
            )
        # 'depth', 'sequence_number', 'visual', 'data'
        assert image.depth == 24
        return Image.frombytes("RGB", (capture_rect.width, capture_rect.height), image.data, "raw", "BGRX")

    def fake_input(self, event_type: int, detail: int = 0, x: int = 0, y: int = 0) -> None:
        with self._lock:
            fake_input(self._display, event_type, detail, x=x, y=y)
            self._display.sync()


class Screen:
    def __init__(self, display, screen):
        self._display = display
        self._screen = screen
        self._root_window = Window(display, screen, self._screen.root)

    @property
    def size(self) -> Tuple[int, int]:
        return self._screen.width_in_pixels, self._screen.height_in_pixels

    @property
    def root_window(self) -> Window:
        return self._root_window


class Display:
    def __init__(self, display_name: Optional[str] = None):
        self._display = Xlib.display.Display(display_name)

    def screen(self, display_no: Optional[int] = None) -> Screen:
        return Screen(self._display, self._display.screen())

    def screen_count(self) -> int:
        return self._display.screen_count()
