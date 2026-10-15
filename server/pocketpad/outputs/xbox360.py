import vgamepad as vg
from .base import Output

B = vg.XUSB_BUTTON
BUTTONS = {
    "A": B.XUSB_GAMEPAD_A, "B": B.XUSB_GAMEPAD_B,
    "X": B.XUSB_GAMEPAD_X, "Y": B.XUSB_GAMEPAD_Y,
    "LB": B.XUSB_GAMEPAD_LEFT_SHOULDER, "RB": B.XUSB_GAMEPAD_RIGHT_SHOULDER,
    "START": B.XUSB_GAMEPAD_START, "BACK": B.XUSB_GAMEPAD_BACK,
    "L3": B.XUSB_GAMEPAD_LEFT_THUMB, "R3": B.XUSB_GAMEPAD_RIGHT_THUMB,
    "UP": B.XUSB_GAMEPAD_DPAD_UP, "DOWN": B.XUSB_GAMEPAD_DPAD_DOWN,
    "LEFT": B.XUSB_GAMEPAD_DPAD_LEFT, "RIGHT": B.XUSB_GAMEPAD_DPAD_RIGHT,
}


class Xbox360Output(Output):
    AXES = {"LX", "LY", "RX", "RY", "LT", "RT"}

    def __init__(self):
        self.pad = vg.VX360Gamepad()
        self.ax = dict.fromkeys(self.AXES, 0.0)
        self.held = set()

    def axis(self, target, value):
        if target in ("LT", "RT"):
            value = max(0.0, min(1.0, value))
        else:
            value = max(-1.0, min(1.0, value))
        self.ax[target] = value

    def button(self, target, pressed):
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
        self.pad.left_trigger_float(a["LT"])
        self.pad.right_trigger_float(a["RT"])
        self.pad.update()

    def reset(self):
        self.ax = dict.fromkeys(self.AXES, 0.0)
        self.held.clear()
        self.pad.reset()
        self.pad.update()
