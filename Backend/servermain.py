import asyncio
import json
import random
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn


STOCKS = ["AAPL", "GOOGL", "AMZN", "MSFT"]

MAX_SUBSCRIPTIONS = 5

# symbol -> set of client_ids
subscriptions: dict[str, set[int]] = {}

# client_id -> set of symbols
client_subscriptions: dict[int, set[str]] = {}

# client_id -> WebSocket
clients: dict[int, WebSocket] = {}


# Initialize prices with a random baseline
stock_prices = {s: 150 + random.uniform(-5, 5) for s in STOCKS}


def subscribe(ws: WebSocket, symbol: str):
    client_id = id(ws)
    if symbol not in STOCKS:
        return
    if symbol in client_subscriptions[client_id]:
        return
    if len(client_subscriptions[client_id]) >= MAX_SUBSCRIPTIONS:
        return
    subscriptions.setdefault(symbol, set()).add(client_id)
    client_subscriptions[client_id].add(symbol)
    print(f"{ws.client} subscribed to {symbol}")





def unsubscribe(ws: WebSocket, symbol: str):
    client_id = id(ws)
    subscriptions.get(symbol, set()).discard(client_id)
    client_subscriptions.get(client_id, set()).discard(symbol)




def cleanup(ws: WebSocket):
    client_id = id(ws)
    for symbol in client_subscriptions.get(client_id, set()):
        subscriptions[symbol].discard(client_id)
    client_subscriptions.pop(client_id, None)
    clients.pop(client_id, None)




# For protecting stock updates during broadcast 
price_lock = asyncio.Lock()


async def stream_updates():
    """Continuously send stock price updates to subscribed clients."""
    while True:
        await asyncio.sleep(1)

        async with price_lock:
            for symbol in STOCKS:
                # Apply random delta
                delta = round(random.uniform(-1, 1), 2)
                stock_prices[symbol] = round(stock_prices[symbol] + delta, 2)

                # Build the update message
                message = json.dumps({
                    "ticker": symbol,
                    "price": stock_prices[symbol],
                    "change": delta
                })

                # Send message only to subscribed clients
                for client_id in subscriptions.get(symbol, set()).copy():
                    ws = clients.get(client_id)
                    if ws is None:
                        continue
                    try:
                        await ws.send_text(message)
                    except:
                        cleanup(ws)





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
app.mount("/app", StaticFiles(directory="frontend/week3", html=True), name="frontend")

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
    client_id = id(ws)
    clients[client_id] = ws
    client_subscriptions[client_id] = set()
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
      cleanup(ws)




if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8000)
 