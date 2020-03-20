import asyncio
import threading

import numpy

from momo.screen_capture import Display, Window
from momo.webrtc import ScreenCaptureTrack, WebRTCClient


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
    window = screen.root_window
    connection = WebRTCClient(track)

    loop = asyncio.get_event_loop()

    await connection.connect()
    cancelled = threading.Event()
    try:
        t = loop.run_in_executor(None, capture_and_send, window, track, cancelled)
        await connection.wait_until_complete()
        cancelled.set()
        await t
    finally:
        await connection.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
