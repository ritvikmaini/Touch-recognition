import math
from tuio_touch_tracker.touch import Touch, delete_duplicates


def test_distance_is_euclidean():
    a = Touch(0, 0, 1)
    b = Touch(3, 4, 1)
    assert a.calc_distance(b) == 5.0


def test_nearest_skips_self_and_returns_closest():
    a = Touch(0, 0, 1); a.set_id(1)
    near = Touch(1, 1, 1); near.set_id(2)
    far = Touch(10, 10, 1); far.set_id(3)
    assert a.nearest([a, near, far]).get_id() == 2


def test_nearest_on_empty_returns_placeholder_id_zero():
    a = Touch(0, 0, 1); a.set_id(1)
    assert a.nearest([a]).get_id() == 0


def test_equality_and_hash_by_id():
    a = Touch(0, 0, 1); a.set_id(5)
    b = Touch(9, 9, 2); b.set_id(5)
    assert a == b
    assert hash(a) == hash(b)


def test_delete_duplicates_keeps_first_per_id():
    a = Touch(0, 0, 1); a.set_id(1)
    b = Touch(1, 1, 1); b.set_id(1)
    c = Touch(2, 2, 1); c.set_id(2)
    result = delete_duplicates([a, b, c])
    assert [t.get_id() for t in result] == [1, 2]
