import asyncio
import json
import logging
from typing import Optional

from aiortc import RTCConfiguration, RTCDataChannel, RTCIceServer, RTCPeerConnection, RTCSessionDescription

from x2webrtc import models
from x2webrtc.input import InputHandler
from x2webrtc.track import ScreenCaptureTrack

_logger = logging.getLogger(__name__)


class WebRTCClient:
    def __init__(self, track: ScreenCaptureTrack, input_handler: InputHandler):
        self._pc = RTCPeerConnection(RTCConfiguration(iceServers=[RTCIceServer("stun:stun.l.google.com:19302")]))
        self._track = track
        self._input_handler = input_handler

        self._pc.addTrack(self._track)
        self._control_channel: RTCDataChannel = self._pc.createDataChannel("control")
        self._control_channel.on("message", self._on_message)

        self._lock = asyncio.Lock()
        self._connection_task: Optional[asyncio.Task[None]] = None

    async def _run(self):
        self._track.active = True
        try:
            # TODO(igarashi): Handle connection closed
            while True:
                if self._pc.sctp.transport.state == "closed":
                    _logger.warn("stream cancelled by remote")
                    break

                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            _logger.warn("operation cancelled")
        finally:
            self._connection_task = None
            self._track.active = False
            await self._pc.close()

    def _on_message(self, message_str: str) -> None:
        try:
            data = json.loads(message_str)
            message = models.from_dict(data)
            if isinstance(message, models.InputReport):
                self._input_handler.send(message)

        except Exception:
            _logger.exception("got an unexpected exception")

    async def _establish_connection(self):
        loop = asyncio.get_event_loop()

        # NOTE(igarashi): Start signaling from client
        await self._pc.setLocalDescription(await self._pc.createOffer())

        # TODO(igarashi): Send offer somehow
        from aiortc.contrib.signaling import CopyAndPasteSignaling

        self.signaling = CopyAndPasteSignaling()
        await self.signaling.connect()
        print("[NOTE] The online viewer is available at https://bonprosoft.github.io/x2webrtc/online_viewer/ ")
        await self.signaling.send(self._pc.localDescription)
        # TODO(igarashi): Receive answer and ice somehow
        obj = await self.signaling.receive()
        assert isinstance(obj, RTCSessionDescription)
        await self._pc.setRemoteDescription(obj)
        _logger.info("remote description received")
        self._connection_task = loop.create_task(self._run())

    async def connect(self) -> None:
        await self._establish_connection()

    async def wait_until_complete(self) -> None:
        t = self._connection_task
        if t is None:
            return

        await t

    async def disconnect(self) -> None:
        _logger.info("disconnecting WebRTC peer connection")
        await self._pc.close()
