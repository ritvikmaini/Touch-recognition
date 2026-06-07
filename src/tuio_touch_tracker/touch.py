import math


class Touch:
    def __init__(self, x, y, frame):
        self._x = x
        self._y = y
        self._id = 0
        self._frame = frame

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_id(self):
        return self._id

    def set_id(self, id):
        self._id = id

    def get_frame(self):
        return self._frame

    def calc_distance(self, other):
        return math.sqrt((self._x - other.get_x()) ** 2 + (self._y - other.get_y()) ** 2)

    def nearest(self, touch_list):
        nearest_touch = Touch(0, 0, 0)
        min_distance = float('inf')
        for touch in touch_list:
            if touch is not self:
                distance = self.calc_distance(touch)
                if distance < min_distance:
                    min_distance = distance
                    nearest_touch = touch
        return nearest_touch

    def __eq__(self, other):
        if not isinstance(other, Touch):
            return False
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)


def delete_duplicates(touch_list):
    seen_ids = set()
    result = []
    for touch in touch_list:
        if touch.get_id() not in seen_ids:
            seen_ids.add(touch.get_id())
            result.append(touch)
    return result
