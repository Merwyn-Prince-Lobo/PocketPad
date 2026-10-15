import argparse, asyncio, json, socket, time
from . import PORT, DISCOVERY_PORT, PROTOCOL_VERSION, __version__
from .profiles import load_profile, shape
from .outputs import make_output

TIMEOUT = 0.5  # seconds without packets -> release everything (no stuck throttle!)


def lan_ip() -> str:
    """IP of the interface with the default route (avoids VMware/WSL adapters)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class Controller:
    def __init__(self, profile):
        self.profile = profile
        self.out = make_output(profile.output)
        self.seq = -1
        self.last = 0.0
        self.peer = None

    def handle(self, data: bytes, addr):
        try:
            pkt = json.loads(data)
            if pkt.get("v") != PROTOCOL_VERSION:
                return
            seq, ctrl = int(pkt["s"]), pkt["c"]
        except (ValueError, KeyError, TypeError):
            return
        now = time.monotonic()
        if seq <= self.seq and now - self.last < 1.0:
            return  # stale / reordered
        self.seq, self.last = seq, now
        if self.peer != addr[0]:
            self.peer = addr[0]
            print(f"phone connected: {addr[0]}")
        for cid, val in ctrl.items():
            b = self.profile.map.get(cid)
            if b is None:
                continue
            v = float(val)
            if self.out.is_axis(b.target):
                self.out.axis(b.target, shape(v, b))
            else:
                self.out.button(b.target, v >= b.threshold)
        self.out.flush()

    def check_timeout(self):
        if self.peer and time.monotonic() - self.last > TIMEOUT:
            self.out.reset()
            print("phone disconnected (timeout), inputs released")
            self.peer = None


class ControlProto(asyncio.DatagramProtocol):
    def __init__(self, ctl): self.ctl = ctl
    def datagram_received(self, data, addr): self.ctl.handle(data, addr)


class DiscoveryProto(asyncio.DatagramProtocol):
    def __init__(self, profile): self.profile = profile
    def connection_made(self, transport): self.t = transport

    def datagram_received(self, data, addr):
        if data.strip() == b"POCKETPAD_DISCOVER":
            reply = {"app": "pocketpad", "v": PROTOCOL_VERSION, "name": socket.gethostname(),
                     "port": PORT, "profile": self.profile.name}
            self.t.sendto(json.dumps(reply).encode(), addr)


async def run(profile_ref: str):
    profile = load_profile(profile_ref)
    ctl = Controller(profile)
    loop = asyncio.get_running_loop()
    await loop.create_datagram_endpoint(lambda: ControlProto(ctl), local_addr=("0.0.0.0", PORT))
    await loop.create_datagram_endpoint(lambda: DiscoveryProto(profile),
                                        local_addr=("0.0.0.0", DISCOVERY_PORT), allow_broadcast=True)
    print(f"PocketPad {__version__} | profile: {profile.name} ({profile.output})")
    print(f"phone -> {lan_ip()}:{PORT}   (UDP)   Ctrl+C to quit")
    try:
        while True:
            await asyncio.sleep(0.1)
            ctl.check_timeout()
    finally:
        ctl.out.reset()


def cli():
    ap = argparse.ArgumentParser(prog="pocketpad")
    ap.add_argument("-p", "--profile", default="assetto-corsa",
                    help="profile name (from /profiles) or path to a .json")
    args = ap.parse_args()
    try:
        # selector loop: proactor's UDP support is flaky on Windows
        asyncio.run(run(args.profile), loop_factory=asyncio.SelectorEventLoop)
    except KeyboardInterrupt:
        print("\nbye")
