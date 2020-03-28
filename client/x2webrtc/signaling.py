import importlib.machinery
import logging
import pathlib
import types
from typing import Optional

from aiortc import RTCPeerConnection, RTCSessionDescription

from x2webrtc.plugin import SignalingPlugin

_logger = logging.getLogger(__name__)
SIGNALING_PLUGIN_ENVKEY = "X2WEBRTC_SIGNALING"


class CopyAndPasteSignaling(SignalingPlugin):
    async def __call__(self, pc: RTCPeerConnection) -> bool:
        from aiortc.contrib.signaling import CopyAndPasteSignaling as Impl

        await pc.setLocalDescription(await pc.createOffer())
        signaling = Impl()
        await signaling.connect()
        print("[NOTE] The online viewer is available at https://bonprosoft.github.io/x2webrtc/online_viewer/ ")
        await signaling.send(pc.localDescription)
        # TODO(igarashi): Receive answer and ice somehow
        obj = await signaling.receive()
        assert isinstance(obj, RTCSessionDescription)
        await pc.setRemoteDescription(obj)
        _logger.info("remote description received")

        return True


def _load_plugin(py_path: pathlib.Path) -> SignalingPlugin:
    _logger.info("loading {} as a plugin".format(py_path))
    if not py_path.exists() or py_path.is_dir():
        raise RuntimeError("invalid plugin path")

    try:
        loader = importlib.machinery.SourceFileLoader("plugin", str(py_path))
        module = types.ModuleType(loader.name)
        loader.exec_module(module)
        entry_point = getattr(module, "plugin", None)
        if entry_point is None or not callable(entry_point):
            raise RuntimeError("cannot find `plugin` method in the plugin")

        ret = entry_point()
        if not isinstance(ret, type) or not issubclass(ret, SignalingPlugin):
            raise RuntimeError("`plugin` method must return a subclass of `SignalingPlugin`")

        return ret()
    except Exception:
        _logger.exception("got an unexpected error")
        raise


def get_signaling_method(plugin_path: Optional[pathlib.Path] = None) -> SignalingPlugin:
    if plugin_path is not None:
        return _load_plugin(plugin_path)

    _logger.info("use the default signaling method: copy_and_paste_signaling")
    return CopyAndPasteSignaling()
