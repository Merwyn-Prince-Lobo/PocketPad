"""Profile = which virtual device + how each app control id maps to a target."""
import json
from dataclasses import dataclass, field
from pathlib import Path

PROFILE_DIR = Path(__file__).resolve().parents[2] / "profiles"


@dataclass
class Binding:
    target: str
    invert: bool = False
    deadzone: float = 0.0
    gamma: float = 1.0
    scale: float = 1.0
    threshold: float = 0.5  # for button targets


@dataclass
class Profile:
    name: str
    output: str
    map: dict = field(default_factory=dict)


def load_profile(ref: str) -> Profile:
    p = Path(ref)
    if not p.exists():
        p = PROFILE_DIR / (ref if ref.endswith(".json") else ref + ".json")
    if not p.exists():
        raise SystemExit(f"profile not found: {ref}  (looked in {PROFILE_DIR})")
    raw = json.loads(p.read_text(encoding="utf-8"))
    bindings = {cid: Binding(**cfg) for cid, cfg in raw["map"].items()}
    return Profile(raw.get("name", p.stem), raw["output"], bindings)


def shape(v: float, b: Binding) -> float:
    """Apply invert / deadzone / gamma / scale to a raw control value."""
    if b.invert:
        v = -v
    s = -1.0 if v < 0 else 1.0
    a = abs(v)
    if a < b.deadzone:
        return 0.0
    a = ((a - b.deadzone) / (1 - b.deadzone)) if b.deadzone < 1 else 0.0
    a = (a ** b.gamma) * b.scale
    return s * a
