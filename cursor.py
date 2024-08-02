"""Query and control cursor position.
Return cursor coordinates relative to cursor resolution 2^16 x 2^16.
Move cursor to specified coordinates.
"""

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


def set_cursor_position(x, y):
    result = ctypes.windll.user32.SetCursorPos(x, y)
    if result:
        print(f"Cursor moved to ({x}, {y})")
        return True
    else:
        print("Failed to move cursor")
        return False


# Example usage
if __name__ == "__main__":
    # Get current cursor position
    current_position = get_cursor_position()
    print(f"Current position: {current_position}")

    # Move cursor to (100, 100)
    set_cursor_position(100, 100)

    # Verify new cursor position
    new_position = get_cursor_position()
    print(f"New position: {new_position}")
