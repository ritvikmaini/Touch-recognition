"""TUIO cursor event sending. Wraps pythontuio's TuioServer.

Behavior preserved verbatim from the original blob.py, including the
known quirks documented in the README (e.g. finger_up removing an int
from a list of Cursor objects).
"""

from pythontuio import TuioServer, Cursor


def normalize(x, y, width, height):
    return (x / width), (y / height)


def finger_down(cursor_id, x, y, server, width, height):
    nx, ny = normalize(x, y, width, height)
    cursor = Cursor(cursor_id)
    cursor.position = (nx, ny)
    server.cursors.append(cursor)
    return server


def finger_moved(cursor_id, x, y, server, width, height):
    nx, ny = normalize(x, y, width, height)
    cursor = next((c for c in server.cursors if c.session_id == cursor_id), None)
    if cursor:
        cursor.position = (nx, ny)
    return server


def finger_up(cursor_id, server):
    # Preserved as-is from the original (see README known limitations).
    if cursor_id in server.cursors:
        server.cursors.remove(cursor_id)
        print(f"REMOVE: Cursor ID: {cursor_id}")
    return server


def print_touch_events(current, server):
    for cursor in server.cursors:
        for touch in current:
            if cursor.session_id == touch.get_id():
                print(f"Cursor ID: {touch.get_id()} X: {touch.get_x()} Y: {touch.get_y()}")


def new_server(host="127.0.0.1", port=3333):
    return TuioServer(host, port)
