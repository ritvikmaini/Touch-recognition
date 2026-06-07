# TUIO Touch Tracker — Publishing Polish Design

**Date:** 2026-06-07
**Author:** Ritvik Maini
**Status:** Approved

## Goal

Take the existing two-file prototype (`blob.py`, `touch.py`) and prepare it for
public publishing: a clean modular Python package, a visually impressive
README that frames the project as a **TUIO source for touch recognition**, and
the supporting files (LICENSE, manifest, fixed git hygiene) that make the repo
self-contained and runnable out of the box.

## Decisions (from brainstorming)

- **Refactor scope:** Modularize the monolithic `blob.py` into a package.
  Preserve the existing algorithm and runtime behavior **exactly** — no logic
  fixes. (Known quirks documented in README "Known limitations" instead.)
- **README:** Visual showcase, TUIO-focused. Demo media at top, badges,
  pipeline diagram, quickstart, how-it-works, configuration, structure.
- **Demo media:** Generate a screenshot + GIF from `mt_camera_raw.mp4` via a
  new headless output mode.
- **License:** MIT, © Ritvik Maini.
- **Project name:** TUIO Touch Tracker. Package: `tuio_touch_tracker`.

## Target structure

```
TUIO-Touch-Tracker/
├── README.md
├── LICENSE                      # MIT © Ritvik Maini
├── requirements.txt
├── pyproject.toml               # pip install -e . + `tuio-touch-tracker` CLI
├── .gitignore                   # fixed: stop ignoring sample video & data/
├── src/
│   └── tuio_touch_tracker/
│       ├── __init__.py
│       ├── touch.py             # Touch model + delete_duplicates (unchanged)
│       ├── detection.py         # bg-subtraction → contours → ellipses → Touch
│       ├── tracking.py          # nearest-neighbor ID assignment + existence
│       ├── tuio_sender.py       # fingerDown/Moved/Up, normalize, TuioServer wrap
│       ├── visualization.py     # annotate/draw frame
│       ├── pipeline.py          # main loop orchestration
│       └── cli.py               # argparse entry point + __main__
├── data/
│   └── mt_camera_raw.mp4        # committed sample (symlink hack removed)
└── docs/
    ├── media/                   # demo.gif + screenshot.png (generated)
    └── superpowers/specs/       # this doc
```

Rationale: `src`-layout is the modern packaging standard — avoids import-path
surprises and signals packaging competence.

## Module breakdown (behavior preserved)

Same algorithm as `blob.py` today, separated by responsibility; each module is
independently understandable and testable.

- **`detection.py`** — `Detector` holds the grayscale reference frame.
  `detect(frame) -> list[Touch]` runs absdiff → blur(20,20) → highpass absdiff →
  threshold(10,255) → `findContours(RETR_CCOMP)` → filter `contourArea > 30` and
  `len(contour) > 4` → `fitEllipse` → `Touch(cx, cy, frame_no)`.
  (Source: blob.py lines 62–69, 117–132.)
- **`tracking.py`** — `assign_ids(current, previous, id_counter)` reuses the
  nearest previous touch's id when `nearest.get_id() > 0`, else increments the
  counter. Includes `existence(touch, previous)`.
  (Source: blob.py lines 70–75, 126–131.)
- **`tuio_sender.py`** — wraps `TuioServer`; `finger_down/moved/up`,
  `normalize(x, y, width, height)`, `send`, `print_touch_events`.
  (Source: blob.py lines 7–25, 76–80.)
- **`visualization.py`** — `annotate(frame, touches, frame_no, ms) -> frame`
  draws ID/X/Y text and nearest-neighbor lines + distances. Display vs. save is
  decoupled from drawing.
  (Source: blob.py lines 26–61.)
- **`pipeline.py`** — wires capture → detect → assign_ids → TUIO diff
  (down/moved/up) → annotate. Owns the `while` loop and frame bookkeeping.
  (Source: blob.py lines 82–183.)

## CLI + headless mode

`cli.py` via argparse. Defaults match today's hard-coded values, so a plain run
is behaviorally identical.

```
tuio-touch-tracker \
    --video data/mt_camera_raw.mp4 \
    --min-area 30 --threshold 10 \
    --tuio-host 127.0.0.1 --tuio-port 3333 \
    --display / --no-display \
    --save-frames docs/media/frames
```

All `cv2.imshow`/`cv2.waitKey` calls are guarded behind `--display` (default
on). `--save-frames DIR` writes annotated frames to disk, enabling headless
runs (servers/CI) and demo-media generation.

## README outline (visual showcase, TUIO-focused)

1. Title + one-liner: real-time multitouch blob tracking that streams TUIO
   cursor events to any TUIO-compatible app.
2. Demo GIF (top).
3. Badges: Python, license, OpenCV, TUIO.
4. What it does / Why TUIO — drop-in touch source for TUIO clients
   (interactive tables, Processing/openFrameworks/Pure Data).
5. Pipeline diagram (Mermaid): Video → Background subtraction → Blob detection
   → Tracking → TUIO/OSC.
6. Quickstart — install + run in ~3 commands.
7. How it works — CV pipeline explained with the screenshot.
8. Configuration — CLI flags table.
9. Project structure, Roadmap / Known limitations, License.

## Supporting files & git hygiene

- `requirements.txt`: opencv-python, numpy, python-tuio (pulls python-osc).
- `pyproject.toml`: package metadata + `tuio-touch-tracker` console script.
- MIT `LICENSE`.
- `.gitignore`: keep ignoring `.venv/ __pycache__/ *.pyc .idea/ .DS_Store`;
  **stop** ignoring `data/` and the sample `*.mp4`.
- Track the moved `touch.py` (currently untracked → would break a clone).
- Remove the `data/mt_camera_raw.mp4` symlink and the duplicate root video;
  keep a single real file at `data/mt_camera_raw.mp4`.

## Known limitations (documented, not fixed)

Preserved exactly per scope decision; noted in README Roadmap:

- `finger_up` removes a cursor id (int) from a list of `Cursor` objects — a
  no-op as written.
- `server.cursors.clear()` runs every frame after sending.
- TUIO bundles only start sending after frame 49.

## Success criteria

- `pip install -e .` then `tuio-touch-tracker` runs the pipeline identically to
  today's `python blob.py`.
- `--no-display --save-frames` produces annotated frames headlessly.
- Repo is self-contained: a fresh clone runs without missing files.
- README renders with working demo media, diagram, and badges.
