import json

from x2webrtc.models import (ButtonEventKind, MouseButtonEvent,
                             MouseButtonKind, MouseMoveEvent, ScreenEvents,
                             from_dict, to_dict)


def test_convert_convertback():
    a = MouseMoveEvent(10, 20)
    b = MouseButtonEvent(MouseButtonKind.LEFT_BUTTON, ButtonEventKind.BUTTON_DOWN)
    c = MouseButtonEvent(MouseButtonKind.LEFT_BUTTON, ButtonEventKind.BUTTON_UP)
    data = ScreenEvents([a, b, c])
    serialized = json.dumps(to_dict(data))

    deserialized = from_dict(json.loads(serialized))
    assert deserialized == data
