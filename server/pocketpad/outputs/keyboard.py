"""Keyboard output via SendInput scancodes (works in most games, Windows only).
Button target: a key name, e.g. "W", "SPACE", "LSHIFT", "UP".
Axis target: "NEG|POS" e.g. "A|D" -> A when value < -0.3, D when value > 0.3."""
import ctypes
from ctypes import wintypes
from .base import Output

SC = {c: s for c, s in zip("QWERTYUIOP", range(0x10, 0x1A))}
SC.update({c: s for c, s in zip("ASDFGHJKL", range(0x1E, 0x27))})
SC.update({c: s for c, s in zip("ZXCVBNM", range(0x2C, 0x33))})
SC.update({str(n): 0x02 + (n - 1) % 10 for n in range(1, 10)}); SC["0"] = 0x0B
SC.update({"ESC": 0x01, "TAB": 0x0F, "ENTER": 0x1C, "SPACE": 0x39,
           "LSHIFT": 0x2A, "LCTRL": 0x1D, "LALT": 0x38})
EXT = {"UP": 0x48, "DOWN": 0x50, "LEFT": 0x4B, "RIGHT": 0x4D}

KEYUP, SCAN, EXTENDED = 0x0002, 0x0008, 0x0001
PUL = ctypes.POINTER(ctypes.c_ulong)


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", PUL)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", PUL)]


class _I(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("i", _I)]


def _send(key: str, down: bool):
    if key in EXT:
        scan, flags = EXT[key], SCAN | EXTENDED
    elif key in SC:
        scan, flags = SC[key], SCAN
    else:
        return
    if not down:
        flags |= KEYUP
    inp = INPUT(1, _I(ki=KEYBDINPUT(0, scan, flags, 0, None)))
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


class KeyboardOutput(Output):
    def __init__(self):
        self.down = set()

    def is_axis(self, target):
        return "|" in target

    def _set(self, key, pressed):
        key = key.upper()
        if pressed and key not in self.down:
            _send(key, True); self.down.add(key)
        elif not pressed and key in self.down:
            _send(key, False); self.down.discard(key)

    def axis(self, target, value):
        neg, pos = target.split("|")
        self._set(neg, value < -0.3)
        self._set(pos, value > 0.3)

    def button(self, target, pressed):
        self._set(target, pressed)

    def reset(self):
        for k in list(self.down):
            self._set(k, False)
