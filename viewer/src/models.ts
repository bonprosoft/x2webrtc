
export class MouseMoveEvent {
    kind: "mouse-move";
    x: number;
    y: number;
}

export enum MouseButtonKind {
    Left = 0,
    Middle = 1,
    Right = 2,
}

export enum ButtonEventKind {
    ButtonDown = 0,
    ButtonUp = 1,
}

export class MouseButtonEvent {
    kind: "mouse-button";
    button_kind: MouseButtonKind;
    event_kind: ButtonEventKind;
}

export type ScreenEvent = MouseMoveEvent | MouseButtonEvent;

export class EventReport {
    kind: "event";
    events: ScreenEvent[];
}