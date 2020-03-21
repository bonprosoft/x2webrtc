import fractions
import queue
import time
from typing import Optional

import numpy
from aiortc.mediastreams import MediaStreamTrack
from av import VideoFrame

from x2webrtc.timer import Timer

VIDEO_TIME_BASE = fractions.Fraction(1, 1000)


def _create_initial_frame(width: int = 640, height: int = 480) -> VideoFrame:
    img = numpy.zeros((width, height, 3), dtype=numpy.uint8)
    return VideoFrame.from_ndarray(img, format="rgb24")


class ScreenCaptureTrack(MediaStreamTrack):  # type: ignore

    kind = "video"

    def __init__(self, fps: int = 30, max_buf_sec: float = 1.0) -> None:
        super().__init__()

        self._fps = fps
        self._queue: "queue.Queue[VideoFrame]" = queue.Queue(int(fps * max_buf_sec))
        self._last_frame = _create_initial_frame()
        self._sender_timer = Timer(fps)
        self._receiver_timer = Timer(fps)

        self._start: Optional[float] = None
        self._active: bool = False

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        self._active = value

    def wait_for_next_put(self) -> None:
        self._sender_timer.wait()

    def put_frame(self, img: numpy.ndarray) -> None:
        if not self.active or self.readyState != "live":
            return

        frame = VideoFrame.from_ndarray(img, format="rgb24")
        try:
            self._queue.put_nowait(frame)
        except queue.Full:
            # NOTE(igarashi): might be either a bug of Timer (i.e. diff >> duration) or a delay of recv()
            self._sender_timer.reset_throttle()
            time.sleep(0.1)

    async def recv(self) -> VideoFrame:
        # NOTE(igarashi): If there is no available frames in the queue,
        # put the last frame we have already sent.
        await self._receiver_timer.wait_async()
        current = time.time()
        if self._start is None:
            self._start = current

        diff = current - self._start

        try:
            frame = self._queue.get_nowait()
            self._last_frame = frame
        except queue.Empty:
            frame = self._last_frame

        frame.pts = int(diff / VIDEO_TIME_BASE)
        frame.time_base = VIDEO_TIME_BASE
        return frame
