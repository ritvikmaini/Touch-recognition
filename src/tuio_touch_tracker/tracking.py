"""Nearest-neighbor touch ID assignment across frames."""

from .touch import Touch


def assign_ids(current, previous, id_counter):
    """Assign each current touch an id by nearest match in previous frame.

    Reuses the nearest previous touch's id when one exists (id > 0),
    otherwise allocates a fresh id. Returns (current, id_counter).
    Behavior preserved from the original blob.py loop.
    """
    for touch in current:
        nearest_touch = touch.nearest(previous)
        if nearest_touch.get_id() > 0:
            touch.set_id(nearest_touch.get_id())
        else:
            id_counter += 1
            touch.set_id(id_counter)
    return current, id_counter


def existence(obj, previous):
    """True if a touch with obj's id exists in previous."""
    for touch in previous:
        if obj.get_id() == touch.get_id():
            return True
    return False
