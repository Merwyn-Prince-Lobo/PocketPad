"""Pretend to be the phone. Usage: python tools/fake_client.py [host]
Sweeps steering, pulses gas, taps 'up' every 2s. Great for testing without the app."""
import json, math, socket, sys, time

host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# discovery test
s.settimeout(0.5); s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
try:
    s.sendto(b"POCKETPAD_DISCOVER", (host if host != "127.0.0.1" else "127.0.0.1", 9877))
    print("discovery reply:", s.recvfrom(1024)[0].decode())
except OSError:
    print("no discovery reply")

seq, t0 = 0, time.time()
while True:
    t = time.time() - t0
    pkt = {"v": 1, "s": seq, "c": {
        "steer": math.sin(t), "gas": 1.0 if int(t) % 4 < 2 else 0.0,
        "brake": 0.0, "up": 1.0 if int(t) % 2 == 0 and (t % 1) < 0.2 else 0.0, "down": 0.0}}
    s.sendto(json.dumps(pkt).encode(), (host, 9876))
    seq += 1
    time.sleep(1 / 60)
