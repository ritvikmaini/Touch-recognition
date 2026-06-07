"""Command-line interface for tuio-touch-tracker."""

import argparse

from .pipeline import run


def build_parser():
    p = argparse.ArgumentParser(
        prog="tuio-touch-tracker",
        description="Real-time multitouch blob tracking that streams TUIO cursor events.",
    )
    p.add_argument("--video", default="data/mt_camera_raw.mp4",
                   help="Path to the input video (default: data/mt_camera_raw.mp4)")
    p.add_argument("--threshold", type=int, default=10,
                   help="Binarization threshold (default: 10)")
    p.add_argument("--min-area", type=int, default=30,
                   help="Minimum contour area to count as a touch (default: 30)")
    p.add_argument("--tuio-host", default="127.0.0.1",
                   help="TUIO/OSC host (default: 127.0.0.1)")
    p.add_argument("--tuio-port", type=int, default=3333,
                   help="TUIO/OSC port (default: 3333)")
    p.add_argument("--max-frames", type=int, default=None,
                   help="Stop after N frames (default: run to end)")
    p.add_argument("--save-frames", default=None,
                   help="Directory to write annotated frames to")
    display = p.add_mutually_exclusive_group()
    display.add_argument("--display", dest="display", action="store_true",
                         help="Show OpenCV windows (default)")
    display.add_argument("--no-display", dest="display", action="store_false",
                         help="Run headless, no GUI windows")
    p.set_defaults(display=True)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return run(
        args.video,
        threshold=args.threshold,
        min_area=args.min_area,
        tuio_host=args.tuio_host,
        tuio_port=args.tuio_port,
        display=args.display,
        save_frames=args.save_frames,
        max_frames=args.max_frames,
    )


if __name__ == "__main__":
    main()
