import socketio

# Global Socket.IO Server Instance
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
