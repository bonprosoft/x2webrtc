import pathlib

import pytest

from x2webrtc.signaling import CopyAndPasteSignaling, get_signaling_method

BASE_DIR = pathlib.Path(__file__).resolve().parent


@pytest.mark.asyncio
async def test_get_signaling_method() -> None:
    default = get_signaling_method()
    assert default is not None
    assert isinstance(default, CopyAndPasteSignaling)

    success = get_signaling_method(BASE_DIR / "examples/good_plugin.py")
    assert success is not None
    assert await success(None) is True

    with pytest.raises(RuntimeError) as e:
        get_signaling_method(BASE_DIR / "examples/unknown_plugin.py")

    assert str(e.value) == "invalid plugin path"

    with pytest.raises(RuntimeError) as e:
        get_signaling_method(BASE_DIR / "examples/bad_plugin.py")

    assert str(e.value) == "cannot find `plugin` method in the plugin"

    with pytest.raises(RuntimeError) as e:
        get_signaling_method(BASE_DIR / "examples/bad_plugin2.py")

    assert str(e.value) == "`plugin` method must return a subclass of `SignalingPlugin`"
