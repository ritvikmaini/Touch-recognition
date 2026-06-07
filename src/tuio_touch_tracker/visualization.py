"""Frame annotation: draw touch ids, coordinates, and nearest-neighbor links."""

import cv2


def annotate(frame, touches, frame_no, ms_time):
    """Draw ids/coordinates and nearest-neighbor lines. Returns the frame."""
    for touch in touches:
        base_x = int(touch.get_x()) + 5
        base_y = int(touch.get_y()) - 5

        cv2.putText(frame, "ID:" + str(touch.get_id()), (base_x, base_y),
                    cv2.FONT_HERSHEY_PLAIN, 0.8, (0, 0, 0), 1, 8)
        cv2.putText(frame, "X:" + str(int(touch.get_x())), (base_x, base_y + 10),
                    cv2.FONT_HERSHEY_PLAIN, 0.8, (200, 80, 80), 1, 8)
        cv2.putText(frame, "Y:" + str(int(touch.get_y())), (base_x, base_y + 20),
                    cv2.FONT_HERSHEY_PLAIN, 0.8, (200, 80, 80), 1, 8)

        nearest_touch = touch.nearest(touches)
        if nearest_touch.get_id() > 0:
            cv2.line(frame, (int(touch.get_x()), int(touch.get_y())),
                     (int(nearest_touch.get_x()), int(nearest_touch.get_y())),
                     (200, 200, 200), 1)
            distance = touch.calc_distance(nearest_touch)
            midpoint = ((int(touch.get_x()) + int(nearest_touch.get_x())) // 2,
                        (int(touch.get_y()) + int(nearest_touch.get_y())) // 2)
            cv2.putText(frame, "{:.2f}".format(distance), midpoint,
                        cv2.FONT_HERSHEY_PLAIN, 0.8, (200, 200, 200), 1, 8)

    cv2.putText(frame, "frame #" + str(frame_no), (0, 15),
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, 4)
    cv2.putText(frame, "time per frame: " + str(ms_time * 1000) + "ms", (0, 30),
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, 1)
    return frame
