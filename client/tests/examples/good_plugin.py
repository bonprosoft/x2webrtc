from typing import Type

import aiortc

from x2webrtc.plugin import SignalingPlugin


class SampleSignalingPlugin(SignalingPlugin):

    async def __call__(self, pc: aiortc.RTCPeerConnection) -> bool:
        return True


def plugin() -> Type[SignalingPlugin]:
    return SampleSignalingPlugin
