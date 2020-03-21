
export class MouseMoveEvent {
    kind: "mouse-move";
    x: number;
    y: number;

    constructor(x: number, y: number) {
        this.kind = "mouse-move";
        this.x = Math.floor(x);
        this.y = Math.floor(y);
    }
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

    constructor(button: MouseButtonKind, event: ButtonEventKind) {
        this.kind = "mouse-button";
        this.button_kind = button;
        this.event_kind = event;
    }

}

export type ScreenEvent = MouseMoveEvent | MouseButtonEvent;

export class InputReport {
    kind: "input";
    events: ScreenEvent[];

    constructor(events: ScreenEvent[]) {
        this.kind = "input";
        this.events = events;
    }
}
