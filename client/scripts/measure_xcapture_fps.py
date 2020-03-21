import time
import argparse

from x2webrtc.screen_capture import Display


def main() -> None:
    parser = argparse.ArgumentParser(
        description="measure the performance of the current implementation of screen capture"
    )
    parser.add_argument(
        "-d", "--duration", type=float, default=10.0, help="time duration to measure the performance",
    )
    parser.add_argument(
        "--display", type=str, help="display_name of the X server to connect to (e.g., hostname:1, :1.)"
    )
    args = parser.parse_args()

    display = Display(args.display)
    screen = display.screen()
    window = screen.root_window

    duration = float(args.duration)
    print("start performance measurement of screen capture (duration={} sec.)".format(duration))

    stime = time.time()
    etime = stime + duration
    frames = 0

    while time.time() < etime:
        window.capture()
        frames += 1

    print("DONE.\nfps: {} (duration={} sec.)".format(frames / duration, duration))


if __name__ == "__main__":
    main()
