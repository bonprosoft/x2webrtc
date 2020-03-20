import asyncio
from typing import Optional

from aiortc import RTCDataChannel, RTCIceCandidate, RTCPeerConnection, RTCSessionDescription

from momo.track import ScreenCaptureTrack


class WebRTCClient:
    def __init__(self, track: ScreenCaptureTrack):
        self._pc = RTCPeerConnection()
        self._track = track

        self._pc.addTrack(self._track)
        self._channel: RTCDataChannel = self._pc.createDataChannel("data")

        self._lock = asyncio.Lock()
        self._connection_task: Optional[asyncio.Task[None]] = None

    async def _run(self):
        self._track.active = True
        try:
            # TODO(igarashi): Handle connection closed
            # self._pc.sctp.transport.state == "closed"

            from aiortc.contrib.signaling import BYE

            while True:
                obj = await self.signaling.receive()
                if isinstance(obj, RTCIceCandidate):
                    self._pc.addIceCandidate(obj)
                elif obj is BYE:
                    print("Exiting")
                    break
                else:
                    assert False, type(obj)

        finally:
            self._connection_task = None
            self._track.active = False
            await self._pc.close()

    async def _establish_connection(self):
        loop = asyncio.get_event_loop()

        # NOTE(igarashi): Start signaling from client
        await self._pc.setLocalDescription(await self._pc.createOffer())

        # TODO(igarashi): Send offer somehow
        from aiortc.contrib.signaling import CopyAndPasteSignaling

        self.signaling = CopyAndPasteSignaling()
        await self.signaling.connect()
        await self.signaling.send(self._pc.localDescription)
        # TODO(igarashi): Receive answer and ice somehow
        obj = await self.signaling.receive()
        assert isinstance(obj, RTCSessionDescription)
        await self._pc.setRemoteDescription(obj)
        self._connection_task = loop.create_task(self._run())

    async def connect(self) -> None:
        await self._establish_connection()

    async def wait_until_complete(self) -> None:
        t = self._connection_task
        if t is None:
            return

        await t

    async def disconnect(self) -> None:
        await self._pc.close()
