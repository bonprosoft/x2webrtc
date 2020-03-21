import time

from x2webrtc.screen_capture import Display


def main() -> None:
    display = Display()
    screen = display.screen()
    window = screen.root_window
    stime = time.time()
    etime = stime + 10.0
    frames = 0

    while time.time() < etime:
        window.capture()
        frames += 1

    print("fps: {}".format(frames / 10.0))


if __name__ == "__main__":
    main()
