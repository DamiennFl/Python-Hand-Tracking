"""Query and control cursor position.
Return cursor coordinates relative to cursor resolution 2^16 x 2^16.
Move cursor to specified coordinates.
"""

import ctypes
import random
import time


class _point_t(ctypes.Structure):
    """Cursor point coordinate relative to screen resolution."""

    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004

    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long),
    ]


def get_cursor_position():
    point = _point_t()

    result = ctypes.windll.user32.GetCursorPos(ctypes.pointer(point))
    window_w, window_h = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)

    # point.x : window width == x : 65536
    x = int(point.x)
    y = int(point.y)
    if result:
        print(x, y)
        return (x, y)
    else:
        return None


def set_cursor_position(x, y):
    result = ctypes.windll.user32.SetCursorPos(x, y)
    if result:
        print(f"Cursor moved to ({x}, {y})")
        return True
    else:
        print("Failed to move cursor")
        return False


if __name__ == "__main__":
    while True:
        current_position = get_cursor_position()
        if current_position is not None:
            set_cursor_position(current_position[0], current_position[1])
        time.sleep(0.05)
