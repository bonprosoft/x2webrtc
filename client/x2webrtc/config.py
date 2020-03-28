import dataclasses
import os
import pathlib
from typing import Any, Dict, List, Optional

import dacite
import yaml

CONFIG_ENVKEY = "X2WEBRTC_CONFIG"
CONFIG_PATHS = [".x2webrtc", "~/.x2webrtc"]


@dataclasses.dataclass
class IceServer:
    url: str
    username: Optional[str] = None
    credential: Optional[str] = None


@dataclasses.dataclass
class PeerConnectionConfig:
    ice_servers: List[IceServer]

    @classmethod
    def get_default(cls) -> "PeerConnectionConfig":
        return PeerConnectionConfig([IceServer("stun:stun.l.google.com:19302")])


@dataclasses.dataclass
class Config:
    peer_connection: Optional[PeerConnectionConfig] = None
    signaling_plugin: Optional[pathlib.Path] = None

    def get_peer_connection_config(self) -> PeerConnectionConfig:
        if self.peer_connection is not None:
            return self.peer_connection
        return PeerConnectionConfig.get_default()

    @classmethod
    def get_default(cls) -> "Config":
        return Config(None, None)


def load_config_from_dict(data: Dict[str, Any], base_dir: pathlib.Path) -> Config:
    base_dir = base_dir.resolve()

    def parse_path(p: Any) -> pathlib.Path:
        if isinstance(p, pathlib.Path):
            return p
        elif isinstance(p, str):
            return base_dir / p
        else:
            raise RuntimeError("invalid path: {} was specified".format(p))

    return dacite.from_dict(
        Config, data, config=dacite.Config(type_hooks={pathlib.Path: lambda x: parse_path(x)}, strict=True)
    )


def load_config_from_file(path: pathlib.Path) -> Config:
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    return load_config_from_dict(data, path.parent)


def load_config() -> Config:
    env = os.environ.get(CONFIG_ENVKEY, None)
    if env is not None:
        path = pathlib.Path(env)
        if not path.exists() or not path.is_file():
            raise RuntimeError("an invalid config file was specified in the environment variable")
        return load_config_from_file(path)

    for p in CONFIG_PATHS:
        path = pathlib.Path(p)
        if path.exists() and path.is_file():
            return load_config_from_file(path)

    return Config.get_default()
