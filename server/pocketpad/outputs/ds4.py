# NOTE: untested on real hardware, report bugs!
import vgamepad as vg
from .base import Output

DB = vg.DS4_BUTTONS
D = vg.DS4_DPAD_DIRECTIONS
BUTTONS = {
    "CROSS": DB.DS4_BUTTON_CROSS, "CIRCLE": DB.DS4_BUTTON_CIRCLE,
    "SQUARE": DB.DS4_BUTTON_SQUARE, "TRIANGLE": DB.DS4_BUTTON_TRIANGLE,
    "L1": DB.DS4_BUTTON_SHOULDER_LEFT, "R1": DB.DS4_BUTTON_SHOULDER_RIGHT,
    "SHARE": DB.DS4_BUTTON_SHARE, "OPTIONS": DB.DS4_BUTTON_OPTIONS,
    "L3": DB.DS4_BUTTON_THUMB_LEFT, "R3": DB.DS4_BUTTON_THUMB_RIGHT,
}
DPAD = {
    (1, 0, 0, 0): D.DS4_BUTTON_DPAD_NORTH, (1, 0, 0, 1): D.DS4_BUTTON_DPAD_NORTHEAST,
    (0, 0, 0, 1): D.DS4_BUTTON_DPAD_EAST, (0, 1, 0, 1): D.DS4_BUTTON_DPAD_SOUTHEAST,
    (0, 1, 0, 0): D.DS4_BUTTON_DPAD_SOUTH, (0, 1, 1, 0): D.DS4_BUTTON_DPAD_SOUTHWEST,
    (0, 0, 1, 0): D.DS4_BUTTON_DPAD_WEST, (1, 0, 1, 0): D.DS4_BUTTON_DPAD_NORTHWEST,
}


class DS4Output(Output):
    AXES = {"LX", "LY", "RX", "RY", "L2", "R2"}

    def __init__(self):
        self.pad = vg.VDS4Gamepad()
        self.ax = dict.fromkeys(self.AXES, 0.0)
        self.held = set()
        self.dpad = {"UP": 0, "DOWN": 0, "LEFT": 0, "RIGHT": 0}

    def axis(self, target, value):
        lo = 0.0 if target in ("L2", "R2") else -1.0
        self.ax[target] = max(lo, min(1.0, value))

    def button(self, target, pressed):
        if target in self.dpad:
            self.dpad[target] = int(pressed)
            return
        if target == "PS":
            (self.pad.press_special_button if pressed else self.pad.release_special_button)(
                vg.DS4_SPECIAL_BUTTONS.DS4_SPECIAL_BUTTON_PS)
            return
        btn = BUTTONS.get(target)
        if btn is None:
            return
        if pressed and target not in self.held:
            self.pad.press_button(btn); self.held.add(target)
        elif not pressed and target in self.held:
            self.pad.release_button(btn); self.held.discard(target)

    def flush(self):
        a = self.ax
        self.pad.left_joystick_float(a["LX"], a["LY"])
        self.pad.right_joystick_float(a["RX"], a["RY"])
        self.pad.left_trigger_float(a["L2"])
        self.pad.right_trigger_float(a["R2"])
        d = self.dpad
        self.pad.directional_pad(DPAD.get((d["UP"], d["DOWN"], d["LEFT"], d["RIGHT"]),
                                          D.DS4_BUTTON_DPAD_NONE))
        self.pad.update()

    def reset(self):
        self.ax = dict.fromkeys(self.AXES, 0.0)
        self.held.clear()
        self.dpad = dict.fromkeys(self.dpad, 0)
        self.pad.reset()
        self.pad.update()
