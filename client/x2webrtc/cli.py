import argparse
import asyncio
import logging
import sys
import threading
from typing import Optional, Tuple

import numpy

from x2webrtc.input import InputHandler
from x2webrtc.screen_capture import Display, Screen, Window
from x2webrtc.webrtc import ScreenCaptureTrack, WebRTCClient

_logger = logging.getLogger(__name__)


def forward_screen(window: Window, track: ScreenCaptureTrack, quit: threading.Event) -> None:
    while not quit.is_set():
        try:
            track.wait_for_next_put()
            im = window.capture()
            arr = numpy.asarray(im)
            track.put_frame(arr)
        except Exception:
            _logger.exception("got an unexpected exception")


def _get_target_window(args: argparse.Namespace) -> Tuple[Display, Screen, Window]:
    display = Display(args.display)
    screen = display.screen()
    # TODO(igarashi): Select a window using CLI argument
    target_window = screen.root_window
    return display, screen, target_window


async def start_forward(args: argparse.Namespace) -> None:
    loop = asyncio.get_event_loop()

    display, screen, target_window = _get_target_window(args)
    track = ScreenCaptureTrack()
    input_handler = InputHandler()
    connection = WebRTCClient(track, input_handler)
    quit = threading.Event()

    await connection.connect()
    try:
        # NOTE(igarashi): `forward_screen` might be a CPU-bound task, so we dispatch it to another thread
        forward_screen_task = loop.run_in_executor(None, forward_screen, target_window, track, quit)
        input_handler.set_target(target_window)
        await connection.wait_until_complete()
    finally:
        quit.set()
        await connection.disconnect()
        await forward_screen_task


def print_with_tabs(n_tab: int, s: str) -> None:
    print("{}{}".format(" " * n_tab, s))


def traverse_windows(depth: int, window: Window, props: bool) -> None:
    print_with_tabs(depth * 4, "+ Window {} (owner={})".format(window.id, window.owner_id))
    print_with_tabs(depth * 4 + 2, "- wm_name: {}".format(window.wm_name))
    print_with_tabs(depth * 4 + 2, "- wm_class: {}".format(window.wm_class))
    rect = window.rect
    print_with_tabs(depth * 4 + 2, "- rect: x={}, y={}, w={}, h={}".format(rect.x, rect.y, rect.width, rect.height))
    if props:
        print_with_tabs(depth * 4 + 2, "- properties:")
        for k, v in window.properties.items():
            print_with_tabs(depth * 4 + 4, "* {}: {}".format(k, v))

    children = list(window.get_children())
    if len(children) == 0:
        print_with_tabs(depth * 4 + 2, "- no children")
    else:
        print_with_tabs(depth * 4 + 2, "- {} children:".format(len(children)))
        for child in children:
            traverse_windows(depth + 1, child, props)


async def start_info(args: argparse.Namespace) -> None:
    display = Display(args.display)
    for screen_idx in range(display.screen_count()):
        screen = display.screen(screen_idx)
        screen_size = screen.size
        print_with_tabs(0, "[-] Screen {} (size={}x{})".format(screen_idx, screen_size[0], screen_size[1]))
        traverse_windows(1, screen.root_window, args.props)


def set_logger_verbosity(verbosity: int) -> None:
    loglevel = logging.ERROR
    if verbosity >= 3:
        loglevel = logging.DEBUG
    elif verbosity >= 2:
        loglevel = logging.INFO
    elif verbosity >= 1:
        loglevel = logging.WARN

    handler = logging.StreamHandler()
    logging.getLogger("x2webrtc").setLevel(loglevel)
    logging.getLogger("x2webrtc").addHandler(handler)
    _logger.setLevel(loglevel)
    _logger.addHandler(handler)


def main():
    # NOTE(igarashi): Since `asyncio.run` is unavailable in Python 3.6, we use low-level APIs
    parser = argparse.ArgumentParser(description="x2webrtc")
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="verbose; can be used up to 3 times to increase verbosity",
    )
    subparsers = parser.add_subparsers()

    forward_parser = subparsers.add_parser("forward", help="forward X Window")
    forward_parser.add_argument(
        "--display", type=str, help="display_name of the X server to connect to (e.g., hostname:1, :1.)"
    )
    forward_parser.set_defaults(func=start_forward)

    info_parser = subparsers.add_parser("info", help="show window information of the X server")
    info_parser.add_argument(
        "--display", type=str, help="display_name of the X server to connect to (e.g., hostname:1, :1.)"
    )
    info_parser.add_argument("--props", action="store_true", help="show all properties of each window")
    info_parser.set_defaults(func=start_info)

    args = parser.parse_args()
    if "func" not in args:
        parser.print_help()
        sys.exit(1)

    set_logger_verbosity(args.verbose)

    loop = asyncio.get_event_loop()
    task: Optional[asyncio.Future[None]] = None
    try:
        task = asyncio.ensure_future(args.func(args))
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        if task:
            task.cancel()
            loop.run_until_complete(task)
    finally:
        loop.close()


if __name__ == "__main__":
    main()
