import asyncio
import json
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

symbols = ["AAPL", "GOOGL", "AMZN", "MSFT"]
prices = {symbol: 150 + random.uniform(-5, 5) for symbol in symbols}  # initial prices

connections = []


@app.websocket("/ws")
async def stock_updates(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    print("Client connected!")

    try:
        while True:
            updates = []

            for symbol in symbols:
                # simulate small price change
                change = round(random.uniform(-1, 1), 2)
                prices[symbol] = round(prices[symbol] + change, 2)

                updates.append({
                    "symbol": symbol,
                    "price": prices[symbol],
                    "change": change
                })

            # broadcast to all connections
            for connection in connections:
                await connection.send_text(json.dumps(updates))

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Client disconnected!")
        connections.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
