import asyncio
import websockets

async def test():
    async with websockets.connect("ws://127.0.0.1:8000/ws/echo") as ws:
        await ws.send("Hello from Python!")
        reply = await ws.recv()
        print(reply)

asyncio.run(test())
