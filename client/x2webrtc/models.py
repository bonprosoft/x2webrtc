import enum
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Type, TypeVar, Union, cast

import dacite


@dataclass
class _LiteralUnion:
    # TODO(igarashi): Use typing.Literal to treat those discriminated union classes after dacite supports the feature
    kind: str


@dataclass
class EventBase(_LiteralUnion):
    pass


@dataclass
class MouseMoveEvent(EventBase):
    kind: str = field(default="mouse-move", init=False)
    x: int
    y: int


class MouseButtonKind(enum.IntEnum):
    LEFT_BUTTON = 0
    MIDDLE_BUTTON = 1
    RIGHT_BUTTON = 2


class ButtonEventKind(enum.IntEnum):
    BUTTON_DOWN = 0
    BUTTON_UP = 1


@dataclass
class MouseButtonEvent(EventBase):
    kind: str = field(default="mouse-button", init=False)
    button_kind: MouseButtonKind
    event_kind: ButtonEventKind


EventTypes = Union[MouseMoveEvent, MouseButtonEvent]
EVENT_TYPE_MAP: Dict[str, Type[EventTypes]] = {
    MouseMoveEvent.kind: MouseMoveEvent,
    MouseButtonEvent.kind: MouseButtonEvent,
}


@dataclass
class MessageBase(_LiteralUnion):
    pass


@dataclass
class EventReport(MessageBase):
    kind: str = field(default="event", init=False)
    events: List[EventTypes]


MessageType = Union[EventReport]
MESSAGE_TYPE_MAP: Dict[str, Type[MessageType]] = {
    EventReport.kind: EventReport,
}

T = TypeVar("T")


def _find_type(data: Any, type_map: Mapping[str, Type[T]]) -> Type[T]:
    # NOTE(igarashi): first parse temporarily as _Event
    obj = cast(_LiteralUnion, dacite.from_dict(_LiteralUnion, data, config=dacite.Config(strict=False)))
    if obj.kind not in type_map:
        raise RuntimeError("unknown type: {} [must be one of {}]".format(obj.kind, ", ".join(type_map.keys())))

    return type_map[obj.kind]


def _parse_event(data: Any, type_map: Mapping[str, Type[T]]) -> T:
    ret_type = _find_type(data, type_map)
    ret = dacite.from_dict(ret_type, data, config=dacite.Config(cast=[enum.IntEnum], strict=True))
    return cast(T, ret)


def from_dict(data: Any) -> MessageBase:
    ret_type = _find_type(data, MESSAGE_TYPE_MAP)
    return cast(
        MessageBase,
        dacite.from_dict(
            ret_type,
            data,
            config=dacite.Config(
                type_hooks={
                    EventTypes: lambda x: _parse_event(x, EVENT_TYPE_MAP),  # type: ignore
                },
                cast=[enum.IntEnum],
                strict=True,
            ),
        ),
    )


def to_dict(data: MessageBase) -> Dict[str, Any]:
    return asdict(data)
