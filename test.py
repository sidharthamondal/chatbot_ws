from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json
import uuid

app = FastAPI()

# Function to get or generate a user ID based on the WebSocket connection
def get_user_id(websocket):
    user_id = uuid.uuid4().hex  # Generate a new user ID for every new WebSocket connection
    return user_id

@app.websocket("/ws")
async def chatbot(websocket: WebSocket):
    await websocket.accept()
    user_id = get_user_id(websocket)

    try:
        # Handle incoming messages from the WebSocket connection
        while True:
            await websocket.receive_text()  # Wait for a message but ignore its content
            
            # Define a static response
            static_response = {
                "user_id": user_id,
                "message": "This is a static response. Your message was received, but no dynamic processing is done."
            }

            # Send the static response back to the client
            await websocket.send_json(static_response)

    finally:
        print(f"WebSocket connection with user {user_id} closed")

# Comment this code if running inside docker container
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
