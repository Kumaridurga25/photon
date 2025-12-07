from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws/echo")
async def websocket_endpoint(websocket: WebSocket):
    # Accept the client's WebSocket connection
    await websocket.accept()

    try:
        while True:
            # Receive a message from the client
            message = await websocket.receive_text()

            # Send the same message back (echo)
            await websocket.send_text(f"Echo: {message}")

    except WebSocketDisconnect:
        print("Client disconnected")
