import json, ssl, socket
from aiohttp import web
import vgamepad as vg

B = vg.XUSB_BUTTON
pad = vg.VX360Gamepad()

def reset():
    pad.reset(); pad.update()

async def ws_handler(req):
    ws = web.WebSocketResponse(heartbeat=3)
    await ws.prepare(req)
    print("phone connected")
    prev_u = prev_d = False
    try:
        async for m in ws:
            if m.type != web.WSMsgType.TEXT:
                continue
            d = json.loads(m.data)
            pad.left_joystick_float(max(-1, min(1, d["s"])), 0.0)
            pad.right_trigger_float(float(d["t"]))
            pad.left_trigger_float(float(d["b"]))
            if d["u"] and not prev_u: pad.press_button(B.XUSB_GAMEPAD_RIGHT_SHOULDER)
            if not d["u"] and prev_u: pad.release_button(B.XUSB_GAMEPAD_RIGHT_SHOULDER)
            if d["d"] and not prev_d: pad.press_button(B.XUSB_GAMEPAD_LEFT_SHOULDER)
            if not d["d"] and prev_d: pad.release_button(B.XUSB_GAMEPAD_LEFT_SHOULDER)
            prev_u, prev_d = d["u"], d["d"]
            pad.update()
    finally:
        reset()
        print("phone disconnected")
    return ws

async def index(_):
    return web.FileResponse("index.html")

app = web.Application()
app.add_routes([web.get("/", index), web.get("/ws", ws_handler)])

ip = socket.gethostbyname(socket.gethostname())
print(f"open on phone: https://{ip}:8443")
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain("cert.pem", "key.pem")
web.run_app(app, port=8443, ssl_context=ctx)