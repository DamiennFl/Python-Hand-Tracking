"""Query current cursor position.
Return cursor coordinates relative to cursor resolution 2^16 x 2^16."""

import ctypes


class _point_t(ctypes.Structure):
    """Cursor point coordinate relative to screen resolution."""

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


if __name__ == "__main__":

    pos = get_cursor_position()
    # get current mouse position then x coordinate *2.
    print(pos)
    ctypes.windll.user32.mouse_event(0x0001 + 0x8000, pos[0] * 2, pos[1], 0, 0)
