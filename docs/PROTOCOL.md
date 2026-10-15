# PocketPad protocol v1

## Control (UDP, PC port 9876)
One JSON datagram per tick (60-120 Hz):
```json
{"v": 1, "s": 1234, "c": {"steer": -0.42, "gas": 1.0, "brake": 0.0, "up": 0, "down": 0}}
```
- `v` protocol version, `s` sequence number (increasing; stale packets dropped)
- `c` control id -> value. Axes `-1..1` (pedals `0..1`), buttons `0` or `1`
- The *profile* on the PC decides what each control id does. The app stays dumb.
- No packets for 0.5 s -> server releases all inputs.

## Discovery (UDP, PC port 9877)
App broadcasts `POCKETPAD_DISCOVER`; server replies
`{"app":"pocketpad","v":1,"name":"<pc>","port":9876,"profile":"<name>"}`.
