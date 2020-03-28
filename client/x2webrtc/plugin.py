import abc

import aiortc


class SignalingPlugin(abc.ABC):

    @abc.abstractmethod
    async def __call__(self, pc: aiortc.RTCPeerConnection) -> bool:
        pass
