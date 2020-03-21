import enum
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Type, TypeVar, Union, cast

import dacite


@dataclass
class _LiteralUnion:
    # TODO(igarashi): Use typing.Literal to treat those discriminated union
    # classes after dacite supports the feature
    kind: str


@dataclass
class EventBase(_LiteralUnion):
    pass


@dataclass
class MouseMoveEvent(EventBase):
    kind: str = field(default="mouse-move", init=False)
    x: int
    y: int


class TupleEnum(enum.Enum):
    def get_representative(self):
        return self.value[0]

    def get_value(self):
        return self.value[1]

    @classmethod
    def parse_representative(cls, s):
        for k, entry in cls.__members__.items():
            if entry.get_representative() == s:
                return entry

        raise ValueError("unknown entry: {}".format(s))


class MouseButtonKind(TupleEnum):
    LEFT_BUTTON = ("LEFT", 1)
    MIDDLE_BUTTON = ("MIDDLE", 2)
    RIGHT_BUTTON = ("RIGHT", 3)

    def to_X11(self) -> int:
        return self.get_value()


class ButtonEventKind(enum.Enum):
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
class InputReport(MessageBase):
    kind: str = field(default="input", init=False)
    events: List[EventTypes]


MessageType = Union[InputReport]
MESSAGE_TYPE_MAP: Dict[str, Type[MessageType]] = {
    InputReport.kind: InputReport,
}

T = TypeVar("T")
TTupleEnum = TypeVar("TTupleEnum", bound=TupleEnum)


def _find_type(data: Any, type_map: Mapping[str, Type[T]]) -> Type[T]:
    # NOTE(igarashi): first parse temporarily as _Event
    obj = cast(_LiteralUnion, dacite.from_dict(_LiteralUnion, data, config=dacite.Config(strict=False)))
    if obj.kind not in type_map:
        raise RuntimeError("unknown type: {} [must be one of {}]".format(obj.kind, ", ".join(type_map.keys())))

    return type_map[obj.kind]


def _parse_int(data: Any) -> int:
    if isinstance(data, int):
        return data
    elif isinstance(data, float):
        return int(data)
    else:
        raise RuntimeError("an integer value expected, but got type: {}".format(type(data)))


def _parse_tuple_enum(cls: Type[TTupleEnum], data: Any) -> TTupleEnum:
    return cls.parse_representative(data)


def _parse_event(data: Any, type_map: Mapping[str, Type[T]]) -> T:
    ret_type = _find_type(data, type_map)
    ret = dacite.from_dict(
        ret_type,
        data,
        config=dacite.Config(
            type_hooks={
                int: lambda x: _parse_int(x),
                MouseButtonKind: lambda x: _parse_tuple_enum(MouseButtonKind, x),
            },
            cast=[enum.Enum],
            strict=True,
        ),
    )
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
                    MouseButtonKind: lambda x: _parse_tuple_enum(MouseButtonKind, x),
                    int: lambda x: _parse_int(x),
                },
                cast=[enum.Enum],
                strict=True,
            ),
        ),
    )


def to_dict(data: MessageBase) -> Dict[str, Any]:
    return asdict(data)


def _serialize_object(o: Any) -> Any:
    if isinstance(o, TupleEnum):
        return o.get_representative()
    elif isinstance(o, enum.Enum):
        return o.value

    raise TypeError("{} is not JSON serializable".format(o))


def from_json(s: str) -> MessageBase:
    data = json.loads(s)
    return from_dict(data)


def to_json(data: MessageBase) -> str:
    return json.dumps(to_dict(data), default=_serialize_object)
