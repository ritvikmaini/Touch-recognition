from tuio_touch_tracker.tuio_sender import normalize


def test_normalize_divides_by_dimensions():
    assert normalize(50, 25, width=100, height=50) == (0.5, 0.5)


def test_normalize_origin():
    assert normalize(0, 0, width=640, height=480) == (0.0, 0.0)
