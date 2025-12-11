import asyncio
import json
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

symbols = ["AAPL", "GOOGL", "AMZN", "MSFT"]
prices = {symbol: 150 + random.uniform(-5, 5) for symbol in symbols}

connections = set()
lock = asyncio.Lock()


async def broadcast_prices():
    """Broadcast stock updates every second."""
    while True:
        await asyncio.sleep(1)

        updates = []

        async with lock:
            for symbol in symbols:
                change = round(random.uniform(-1, 1), 2)
                prices[symbol] = round(prices[symbol] + change, 2)

                updates.append({
                    "symbol": symbol,
                    "price": prices[symbol],
                    "change": change
                })

        disconnected = []
        for ws in connections:
            try:
                await ws.send_text(json.dumps(updates))
            except:
                disconnected.append(ws)

        for ws in disconnected:
            connections.remove(ws)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown."""
    global broadcast_task
    broadcast_task = asyncio.create_task(broadcast_prices())
    print("Broadcasting task started!")

    yield  # the app runs here

    broadcast_task.cancel()
    print("Broadcasting task stopped!")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)
    print("Client connected!")

    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        print("Client disconnected!")
        connections.discard(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
