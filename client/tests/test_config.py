import os
import pathlib
import tempfile
from unittest import mock

import x2webrtc.config
from x2webrtc.config import CONFIG_ENVKEY, Config, IceServer, load_config, load_config_from_file

BASE_DIR = pathlib.Path(__file__).resolve().parent


def _assert_good_config(config: Config) -> None:
    assert config.signaling_plugin == pathlib.Path("/tmp/x2webrtc/config.py")
    assert config.peer_connection is not None
    assert config.peer_connection.ice_servers == [
        IceServer("stun:stun.example.com"),
        IceServer("turn:turn.example.com", "shamiko", "momo"),
    ]


def test_load_config_from_file() -> None:
    config = load_config_from_file(BASE_DIR / "examples/good_config.yaml")
    _assert_good_config(config)

    config = load_config_from_file(BASE_DIR / "examples/good_config2.yaml")
    assert config.peer_connection is not None
    assert config.peer_connection.ice_servers == [
        IceServer("stun:stun2.example.com"),
    ]


def test_load_config() -> None:
    config = load_config()
    assert config == Config.get_default()

    with mock.patch.dict(os.environ, {CONFIG_ENVKEY: str(BASE_DIR / "examples/good_config.yaml")}):
        config = load_config()
        _assert_good_config(config)

    with tempfile.TemporaryDirectory() as t:
        tmpdir = pathlib.Path(t)
        config1 = tmpdir / "config1.yaml"
        config2 = tmpdir / "config2.yaml"
        with mock.patch.object(x2webrtc.config, "CONFIG_PATHS", [str(config1), str(config2)]):
            config = load_config()
            assert config == Config.get_default()

            with config1.open("w") as f:
                f.write('signaling_plugin: "hoge/fuga.py"\n')

            # NOTE(igarashi): load_config() would use config1.yaml
            config = load_config()
            assert config.signaling_plugin == tmpdir / "hoge/fuga.py"

            with config2.open("w") as f:
                f.write('signaling_plugin: "/hoge/fuga.py"\n')

            # NOTE(igarashi): load_config() would still use config1.yaml
            config = load_config()
            assert config.signaling_plugin == tmpdir / "hoge/fuga.py"

            config1.unlink()

            # NOTE(igarashi): load_config() would use config2.yaml
            config = load_config()
            assert config.signaling_plugin == pathlib.Path("/hoge/fuga.py")
