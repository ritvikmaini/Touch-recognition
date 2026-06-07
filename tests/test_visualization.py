import numpy as np
from tuio_touch_tracker.touch import Touch
from tuio_touch_tracker.visualization import annotate


def test_annotate_returns_same_shape_and_does_not_crash():
    frame = np.zeros((120, 160, 3), dtype=np.uint8)
    t1 = Touch(40, 40, 1); t1.set_id(1)
    t2 = Touch(80, 80, 1); t2.set_id(2)
    out = annotate(frame, [t1, t2], frame_no=5, ms_time=0.01)
    assert out.shape == frame.shape
