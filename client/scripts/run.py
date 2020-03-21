import asyncio
import threading

import numpy

from x2webrtc.input import InputHandler
from x2webrtc.screen_capture import Display, Window
from x2webrtc.webrtc import ScreenCaptureTrack, WebRTCClient


def capture_and_send(window: Window, track: ScreenCaptureTrack, cancelled: threading.Event) -> None:
    while not cancelled.is_set():
        track.wait_for_next_put()
        im = window.capture()
        arr = numpy.asarray(im)
        track.put_frame(arr)


async def main():
    track = ScreenCaptureTrack()
    display = Display()
    screen = display.screen()
    target_window = screen.root_window

    input_handler = InputHandler()
    connection = WebRTCClient(track, input_handler)
    loop = asyncio.get_event_loop()

    await connection.connect()
    cancelled = threading.Event()
    try:
        t = loop.run_in_executor(None, capture_and_send, target_window, track, cancelled)
        input_handler.set_target(target_window)
        await connection.wait_until_complete()
        cancelled.set()
        await t
    finally:
        await connection.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
