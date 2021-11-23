import websocket
import random
import json

ws = websocket.WebSocket()

ws.connect('ws://localhost:8000/ws/pollData')
for i in range(1000):
    ws.send(json.dumps({'value': random.randint(1, 100)}))

