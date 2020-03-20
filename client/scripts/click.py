from momo.screen_capture import Display, Window


def find_by_name(window: Window, name: int) -> Window:
    props = window.properties
    val = props.get("WM_NAME", None)
    if val is not None and val == name:
        return window

    for c in window.get_children:
        ret = find_by_name(c, name)
        if ret is not None:
            return ret

    return None


def main():
    display = Display()
    screen = display.screen()
    print(screen.size)
    window = screen.root_window
    window.move_to(10, 10)
    window.mouse_down(3)
    window.mouse_up(3)


if __name__ == "__main__":
    main()
