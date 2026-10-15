from .base import Output


def make_output(name: str) -> Output:
    name = name.lower()
    if name == "xbox360":
        from .xbox360 import Xbox360Output
        return Xbox360Output()
    if name == "ds4":
        from .ds4 import DS4Output
        return DS4Output()
    if name == "keyboard":
        from .keyboard import KeyboardOutput
        return KeyboardOutput()
    raise SystemExit(f"unknown output '{name}' (xbox360 | ds4 | keyboard)")
