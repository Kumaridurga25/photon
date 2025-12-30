import asyncio
import json
import random
import os
import httpx
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# =====================
# ENV
# =====================
load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
FINNHUB_URL = "https://finnhub.io/api/v1/quote"

print("DEMO_MODE =", DEMO_MODE)
print("FINNHUB_API_KEY =", "SET" if FINNHUB_API_KEY else "MISSING")

# =====================
# GLOBALS
# =====================
STOCKS = ["AAPL", "GOOGL", "AMZN", "MSFT"]

subscriptions = {}          # symbol -> client_ids
client_subscriptions = {}   # client_id -> symbols
clients = {}                # client_id -> websocket

stock_prices = {s: 150 + random.uniform(-5, 5) for s in STOCKS}
price_lock = asyncio.Lock()

# =====================
# HELPERS
# =====================
def generate_demo_price(old_price):
    delta = round(random.uniform(-1, 1), 2)
    return round(old_price + delta, 2), delta

async def fetch_live_price(symbol):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            res = await client.get(
                FINNHUB_URL,
                params={"symbol": symbol, "token": FINNHUB_API_KEY}
            )

        data = res.json()
        return round(float(data["c"]), 2)

    except Exception as e:
        print(f"Finnhub error for {symbol}: {e}")
        return None

# =====================
# STREAM UPDATES
# =====================
async def stream_updates():
    while True:
        await asyncio.sleep(1)

        async with price_lock:
            for symbol in STOCKS:
                old_price = stock_prices[symbol]

                if DEMO_MODE:
                    price, delta = generate_demo_price(old_price)
                    mode = "demo"
                else:
                    price = await fetch_live_price(symbol)
                    if price is None:
                        continue

                 
                    delta = round(price - old_price, 2)
                    mode = "live"

                stock_prices[symbol] = price

                message = json.dumps({
                    "ticker": symbol,
                    "price": price,
                    "change": delta,
                    "mode": mode
                })

                for client_id in subscriptions.get(symbol, set()).copy():
                    ws = clients.get(client_id)
                    if ws:
                        try:
                            await ws.send_text(message)
                        except:
                            cleanup(ws)

                print(f"{symbol}: {price} ({mode})")

# =====================
# SUBSCRIPTIONS
# =====================
def subscribe(ws, symbol):
    cid = id(ws)
    subscriptions.setdefault(symbol, set()).add(cid)
    client_subscriptions[cid].add(symbol)
    print(f"{ws.client} subscribed to {symbol}")

def cleanup(ws):
    cid = id(ws)
    for symbol in client_subscriptions.get(cid, set()):
        subscriptions[symbol].discard(cid)
    client_subscriptions.pop(cid, None)
    clients.pop(cid, None)

# =====================
# FASTAPI
# =====================
@asynccontextmanager
async def lifespan(app):
    task = asyncio.create_task(stream_updates())
    print("Started stock updater.")
    yield
    task.cancel()
    print("Stopped stock updater.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/app", StaticFiles(directory="frontend/week4", html=True), name="frontend")

@app.websocket("/ws")
async def ws_handler(ws: WebSocket):
    await ws.accept()
    cid = id(ws)
    clients[cid] = ws
    client_subscriptions[cid] = set()
    print("Client connected")

    try:
        while True:
            msg = json.loads(await ws.receive_text())
            if msg["action"] == "subscribe":
                subscribe(ws, msg["symbol"])
    except WebSocketDisconnect:
        cleanup(ws)
        print("Client disconnected")

# =====================
# RUN
# =====================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
