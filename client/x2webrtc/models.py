import enum
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping, Optional, Type, TypeVar, Union, cast

import dacite


@dataclass
class EventBase:
    pass


@dataclass
class MouseMoveEvent(EventBase):
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
    button_kind: MouseButtonKind
    event_kind: ButtonEventKind


EventTypes = Union[MouseMoveEvent, MouseButtonEvent]
EVENT_TYPE_MAP: Dict[str, Type[EventTypes]] = {
    "move": MouseMoveEvent,
    "mouse-button": MouseButtonEvent,
}


@dataclass
class _Event:
    kind: str
    event: Dict[str, Any]


@dataclass
class ScreenEvents:
    events: List[EventTypes]


T = TypeVar("T")


def _parse_config(data: Any, type_map: Mapping[str, Type[T]]) -> T:
    # NOTE(igarashi): first parse temporarily as _Event
    event = cast(_Event, dacite.from_dict(_Event, data))
    if event.kind not in type_map:
        raise RuntimeError("unknown type: {} [must be one of {}]".format(event.kind, ", ".join(type_map.keys())))

    ret_type = type_map[event.kind]
    ret = dacite.from_dict(ret_type, event.event, config=dacite.Config(cast=[enum.IntEnum], strict=True))
    return cast(T, ret)


def from_dict(data: Any) -> ScreenEvents:
    return cast(
        ScreenEvents,
        dacite.from_dict(
            ScreenEvents,
            data,
            config=dacite.Config(
                type_hooks={
                    EventTypes: lambda x: _parse_config(x, EVENT_TYPE_MAP),  # type: ignore
                },
                cast=[enum.IntEnum],
                strict=True,
            ),
        ),
    )


def _to_event_type(event: T, type_map: Mapping[str, Type[T]]) -> _Event:
    # NOTE(igarashi): This method wraps event with _Event without recursion.
    # So if a instance has nested instances, the method only wraps the outer-most instance.
    event_klass = type(event)
    event_kind: Optional[str] = None

    for k, v in type_map.items():
        if v is event_klass:
            event_kind = k
            break
    else:
        raise RuntimeError("type_map doesn't have an entry for {}".format(event_klass))

    assert event_kind is not None
    return _Event(event_kind, asdict(event))


def to_dict(data: ScreenEvents) -> Dict[str, Any]:
    return {
        "events": [asdict(_to_event_type(e, EVENT_TYPE_MAP)) for e in data.events],
    }
