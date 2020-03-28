from typing import Type

import aiortc

from x2webrtc.plugin import SignalingPlugin


class SampleSignalingPlugin(SignalingPlugin):

    async def __call__(self, pc: aiortc.RTCPeerConnection) -> bool:
        return True


def bad_plugin_entry_point() -> Type[SampleSignalingPlugin]:
    return SampleSignalingPlugin
