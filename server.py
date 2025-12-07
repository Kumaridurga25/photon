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

connections = []

@app.websocket("/ws/stocks")
async def stock_updates(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    print("Client connected!")

    try:
        while True:
            update = {
                "symbol": "AAPL",
                "price": round(150 + random.uniform(-1, 1), 2),
                "change": round(random.uniform(-0.5, 0.5), 2),
            }

            for connection in connections:
                await connection.send_text(json.dumps(update))

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Client disconnected!")
        connections.remove(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
