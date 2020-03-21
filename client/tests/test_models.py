from x2webrtc.models import (
    ButtonEventKind,
    InputReport,
    MouseButtonEvent,
    MouseButtonKind,
    MouseMoveEvent,
    from_json,
    to_json,
)


def test_convert_convertback():
    a = MouseMoveEvent(10, 20)
    b = MouseButtonEvent(MouseButtonKind.LEFT_BUTTON, ButtonEventKind.BUTTON_DOWN)
    c = MouseButtonEvent(MouseButtonKind.LEFT_BUTTON, ButtonEventKind.BUTTON_UP)
    data = InputReport([a, b, c])
    serialized = to_json(data)

    deserialized = from_json(serialized)
    assert deserialized == data
