import asyncio
import json
import random
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import httpx
import os
from dotenv import load_dotenv

# --- Load API key ---
load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
FINNHUB_URL = "https://finnhub.io/api/v1/quote"

# --- Globals ---
STOCKS = ["AAPL", "GOOGL", "AMZN", "MSFT"]
MAX_SUBSCRIPTIONS = 5
subscriptions: dict[str, set[int]] = {}
client_subscriptions: dict[int, set[str]] = {}
clients: dict[int, WebSocket] = {}
stock_prices = {s: 150 + random.uniform(-5, 5) for s in STOCKS}
price_lock = asyncio.Lock()


# --- Fetch live price from Finnhub ---
async def fetch_live_price(symbol: str):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(
                FINNHUB_URL,
                params={"symbol": symbol, "token": FINNHUB_API_KEY}
            )
        data = response.json()
        if "c" not in data or data["c"] == 0:
            raise Exception("Invalid price")
        return round(float(data["c"]), 2)
    except Exception as e:
        print(f"Finnhub fetch error for {symbol}: {e}")
        return None


# --- Subscription helpers ---
def subscribe(ws: WebSocket, symbol: str):
    client_id = id(ws)
    if symbol not in STOCKS: return
    if symbol in client_subscriptions[client_id]: return
    if len(client_subscriptions[client_id]) >= MAX_SUBSCRIPTIONS: return
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


# --- Stream updates ---
async def stream_updates():
    while True:
        await asyncio.sleep(1)

        async with price_lock:
            # Fetch all symbols concurrently
            tasks = [fetch_live_price(symbol) for symbol in STOCKS]
            results = await asyncio.gather(*tasks)

            for symbol, live_price in zip(STOCKS, results):
                old_price = stock_prices.get(symbol, 150)

                if live_price is not None and live_price != old_price:
                    price = live_price
                    delta = round(price - old_price, 2)
                else:
                    # fallback to random simulated change
                    delta = round(random.uniform(-1, 1), 2)
                    price = round(old_price + delta, 2)

                stock_prices[symbol] = price

                message = json.dumps({
                    "ticker": symbol,
                    "price": price,
                    "change": delta
                })

                for client_id in subscriptions.get(symbol, set()).copy():
                    ws = clients.get(client_id)
                    if ws is not None:
                        try:
                            await ws.send_text(message)
                        except:
                            cleanup(ws)

                # Debug print
                print(f"Sent {symbol}: {price} (delta {delta})")


# --- App lifespan ---
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    global update_task
    update_task = asyncio.create_task(stream_updates())
    print("Started stock updater.")
    yield
    update_task.cancel()
    print("Stopped stock updater.")


# --- FastAPI setup ---
app = FastAPI(lifespan=app_lifespan)
app.mount("/app", StaticFiles(directory="frontend/week3", html=True), name="frontend")

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


# --- Run ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
