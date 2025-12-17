import asyncio
import json
import random
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn


STOCKS = ["AAPL", "GOOGL", "AMZN", "MSFT"]
# symbol -> set of WebSocket subscribers
subscriptions: dict[str, set[WebSocket]] = {}


# Initialize prices with a random baseline
stock_prices = {s: 150 + random.uniform(-5, 5) for s in STOCKS}

# Track connected clients and their subscriptions
client_subscriptions: dict[WebSocket, set[str]] = {}

def subscribe(ws: WebSocket, symbol: str):
    if symbol not in STOCKS:
        return
    subscriptions.setdefault(symbol, set()).add(ws)
    client_subscriptions[ws].add(symbol)


def unsubscribe(ws: WebSocket, symbol: str):
    if symbol in subscriptions:
        subscriptions[symbol].discard(ws)
    client_subscriptions[ws].discard(symbol)


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
               "ticker": symbol,       # changed from "symbol" to "ticker"
               "price": stock_prices[symbol],
               "change": delta
               })


        # Try broadcasting to all active clients
        disconnected = []
        for ws in client_subscriptions:
            try:
                await ws.send_text(json.dumps(price_changes))
            except:
                disconnected.append(ws)

        for ws in disconnected:
            client_subscriptions.pop(ws, None)



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
    client_subscriptions[ws] = set()

    print("Client connected.")

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg.get("action") == "subscribe":
             subscribe(ws, msg.get("symbol"))

            elif msg.get("action") == "unsubscribe":
              unsubscribe(ws, msg.get("symbol"))

    except WebSocketDisconnect:
        print("Client disconnected.")
        client_subscriptions.pop(ws, None)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
