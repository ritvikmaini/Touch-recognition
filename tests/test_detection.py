import numpy as np
from tuio_touch_tracker.detection import Detector


def test_detector_finds_a_blob_against_blank_reference():
    # Reference: all black. Frame: a bright filled disk -> one blob.
    h, w = 120, 160
    reference = np.zeros((h, w), dtype=np.uint8)
    frame = np.zeros((h, w), dtype=np.uint8)
    import cv2
    cv2.circle(frame, (80, 60), 18, 255, -1)

    det = Detector(reference)
    touches = det.detect(frame, frame_no=1)

    assert len(touches) >= 1
    # Blob center should be near the drawn circle center.
    t = touches[0]
    assert abs(t.get_x() - 80) < 15
    assert abs(t.get_y() - 60) < 15
