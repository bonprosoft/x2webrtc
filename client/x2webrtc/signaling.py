import importlib.machinery
import inspect
import logging
import pathlib
import types
from typing import Awaitable, Callable

from aiortc import RTCPeerConnection, RTCSessionDescription

from x2webrtc.config import Config

_logger = logging.getLogger(__name__)
SIGNALING_PLUGIN_ENVKEY = "X2WEBRTC_SIGNALING"
PluginEntryPointType = Callable[[RTCPeerConnection], Awaitable[bool]]


async def copy_and_paste_signaling(pc: RTCPeerConnection) -> bool:
    from aiortc.contrib.signaling import CopyAndPasteSignaling

    await pc.setLocalDescription(await pc.createOffer())
    signaling = CopyAndPasteSignaling()
    await signaling.connect()
    print("[NOTE] The online viewer is available at https://bonprosoft.github.io/x2webrtc/online_viewer/ ")
    await signaling.send(pc.localDescription)
    # TODO(igarashi): Receive answer and ice somehow
    obj = await signaling.receive()
    assert isinstance(obj, RTCSessionDescription)
    await pc.setRemoteDescription(obj)
    _logger.info("remote description received")

    return True


def _load_plugin(py_path: pathlib.Path) -> PluginEntryPointType:
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
    except Exception:
        _logger.exception("got an unexpected error")
        raise

    # NOTE(igarashi): validate the signature of entry_point
    spec = inspect.getfullargspec(entry_point)
    if spec.varargs is not None or spec.varkw is not None:
        # NOTE(igarashi): entry_point accepts either varargs or args
        return entry_point

    if len(spec.args) + len(spec.kwonlyargs) >= 1:
        return entry_point

    raise RuntimeError("entry_point must accept at least one argument")


def get_signaling_method(config: Config) -> PluginEntryPointType:
    plugin = config.signaling_plugin
    if plugin is not None:
        return _load_plugin(plugin)

    _logger.info("use the default signaling method: copy_and_paste_signaling")
    return copy_and_paste_signaling
