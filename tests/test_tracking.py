from tuio_touch_tracker.touch import Touch
from tuio_touch_tracker.tracking import assign_ids, existence


def make(x, y, tid=0):
    t = Touch(x, y, 1)
    t.set_id(tid)
    return t


def test_new_touch_with_no_previous_gets_new_id():
    current = [Touch(5, 5, 1)]
    assigned, counter = assign_ids(current, previous=[], id_counter=0)
    assert assigned[0].get_id() == 1
    assert counter == 1


def test_touch_near_previous_reuses_its_id():
    previous = [make(5, 5, tid=7)]
    current = [Touch(6, 6, 2)]
    assigned, counter = assign_ids(current, previous, id_counter=7)
    assert assigned[0].get_id() == 7
    assert counter == 7  # no new id allocated


def test_existence_true_when_id_present():
    assert existence(make(0, 0, tid=3), [make(9, 9, tid=3)]) is True
    assert existence(make(0, 0, tid=3), [make(9, 9, tid=4)]) is False
