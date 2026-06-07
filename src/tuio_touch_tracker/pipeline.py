"""Main processing loop: video -> detection -> tracking -> TUIO -> render."""

import os
import time

import cv2

from .detection import Detector
from .tracking import assign_ids
from .tuio_sender import (
    finger_down, finger_moved, finger_up, print_touch_events, new_server,
)
from .visualization import annotate


def run(video_path, *, threshold=10, min_area=30, tuio_host="127.0.0.1",
        tuio_port=3333, display=True, save_frames=None, max_frames=None):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    server = new_server(tuio_host, tuio_port)
    previous = []
    id_counter = 0
    current_frame = 0

    if save_frames:
        os.makedirs(save_frames, exist_ok=True)

    ret, frame = cap.read()
    if not ret:
        print("TERMINATION: Camerastream stopped or last frame of video reached.")
        cap.release()
        return id_counter
    reference = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = Detector(reference, threshold=threshold, min_area=min_area)

    condition = True
    while condition:
        ret, frame = cap.read()
        ms_start = time.time()
        current_frame += 1
        if not ret:
            print("TERMINATION: Camerastream stopped or last frame of video reached.")
            break
        if max_frames is not None and current_frame > max_frames:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if display:
            cv2.imshow("original video", gray)

        current = detector.detect(gray, current_frame)
        current, id_counter = assign_ids(current, previous, id_counter)

        currentcopy = current.copy()
        items_to_remove = set()
        for t1 in current:
            for t2 in previous:
                if t1.get_id() == t2.get_id():
                    server = finger_moved(t1.get_id(), t1.get_x(), t1.get_y(),
                                          server, width, height)
                    items_to_remove.add(t1)
        for item in items_to_remove:
            if item in currentcopy:
                currentcopy.remove(item)
        for t1 in previous:
            if t1 not in currentcopy:
                server = finger_up(t1.get_id(), server)
        for t1 in current:
            if t1 not in previous:
                server = finger_down(t1.get_id(), t1.get_x(), t1.get_y(),
                                     server, width, height)

        if current_frame > 49:
            server.send_bundle()
            print_touch_events(current, server)
        server.cursors.clear()

        ms_time = time.time() - ms_start
        annotated = annotate(gray, current, current_frame, ms_time)
        if display:
            cv2.imshow("Result Window", annotated)
        if save_frames:
            cv2.imwrite(os.path.join(save_frames, f"frame_{current_frame:05d}.png"),
                        annotated)

        previous = current.copy()
        if display and (cv2.waitKey(30) & 0xFF == ord("q")):
            print("TERMINATION - q")
            break

    print("the number of unique touches: ", id_counter)
    print("SUCCESS: Program terminated like expected.")
    cap.release()
    if display:
        cv2.destroyAllWindows()
    return id_counter
