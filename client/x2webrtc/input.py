import logging
import threading
from typing import Optional, Tuple

import Xlib.X

from x2webrtc import models
from x2webrtc.screen_capture import Window

_logger = logging.getLogger(__name__)


class InputHandler:
    def __init__(self) -> None:
        self._target: Optional[Window] = None
        self._lock = threading.RLock()

    def set_target(self, target: Optional[Window]) -> None:
        with self._lock:
            self._target = target

    def _translate_coords_from_root(self, x: int, y: int) -> Tuple[int, int]:
        with self._lock:
            assert self._target is not None
            # root = self._target._screen.root
            # ret = root.translate_coords(self._target._window, x, y)
            # NOTE(igarashi): The result of translate_coords from root to the window seems to be the same
            # as the following code.
            rect = self._target.rect
            return x + rect.x, y + rect.y

    def move_to(self, x: int, y: int, relative: bool = True) -> None:
        with self._lock:
            if self._target is None:
                return

            if relative:
                x, y = self._translate_coords_from_root(x, y)

            _logger.debug("send: motion_notidy, pos=({}, {})".format(x, y))
            self._target.fake_input(Xlib.X.MotionNotify, x=x, y=y)

    def mouse_down(self, button: models.MouseButtonKind) -> None:
        with self._lock:
            if self._target is None:
                return

            _logger.debug("send: mouse_down, button={}".format(button))
            self._target.fake_input(Xlib.X.ButtonPress, button.to_X11())

    def mouse_up(self, button: models.MouseButtonKind) -> None:
        with self._lock:
            if self._target is None:
                return

            _logger.debug("send: mouse_up, button={}".format(button))
            self._target.fake_input(Xlib.X.ButtonRelease, button.to_X11())

    def click(self, button: models.MouseButtonKind) -> None:
        with self._lock:
            self.mouse_down(button)
            self.mouse_up(button)

    def send(self, message: models.InputReport) -> None:
        with self._lock:
            for ev in message.events:
                try:
                    if isinstance(ev, models.MouseMoveEvent):
                        self.move_to(ev.x, ev.y, True)
                    elif isinstance(ev, models.MouseButtonEvent):
                        if ev.event_kind == models.ButtonEventKind.BUTTON_UP:
                            self.mouse_up(ev.button_kind)
                        elif ev.event_kind == models.ButtonEventKind.BUTTON_DOWN:
                            self.mouse_down(ev.button_kind)
                        else:
                            _logger.error("unknown event kind: {}".format(ev.event_kind))
                except Exception:
                    _logger.exception("got an unexpected error")
