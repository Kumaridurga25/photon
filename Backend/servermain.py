import asyncio
import json
import random
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn


STOCKS = ["AAPL", "GOOGL", "AMZN", "MSFT"]

# Initialize prices with a random baseline
stock_prices = {s: 150 + random.uniform(-5, 5) for s in STOCKS}

# Connected WebSocket clients
active_clients: set[WebSocket] = set()

# For protecting stock updates during broadcast
price_lock = asyncio.Lock()


async def stream_updates():
    """Continuously send stock price updates to all clients."""
    while True:
        await asyncio.sleep(1)
        price_changes = []

        # Apply random changes
        async with price_lock:
            for symbol in STOCKS:
                delta = round(random.uniform(-1, 1), 2)
                stock_prices[symbol] = round(stock_prices[symbol] + delta, 2)

                price_changes.append({
                    "symbol": symbol,
                    "price": stock_prices[symbol],
                    "change": delta
                })

        # Try broadcasting to all active clients
        disconnected = []
        for ws in active_clients:
            try:
                await ws.send_text(json.dumps(price_changes))
            except:
                disconnected.append(ws)

        for ws in disconnected:
            active_clients.discard(ws)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """Startup/shutdown events for async background tasks."""
    global update_task
    update_task = asyncio.create_task(stream_updates())
    print("Started stock updater.")

    yield

    update_task.cancel()
    print("Stopped stock updater.")


app = FastAPI(lifespan=app_lifespan)

# Serve frontend files
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")

# Allow cross-origin requests (dev only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)


@app.websocket("/ws")
async def websocket_handler(ws: WebSocket):
    await ws.accept()
    active_clients.add(ws)
    print("Client connected.")

    try:
        while True:
            await ws.receive_text()  # keep the connection alive
    except WebSocketDisconnect:
        print("Client disconnected.")
        active_clients.discard(ws)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
