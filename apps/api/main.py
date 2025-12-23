from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn
from contextlib import asynccontextmanager
from apps.api.app.core.socket import sio
from mcp.server.sse import SseServerTransport
from fastapi import Request
from fastapi.responses import Response

# Initialize Socket.IO logic here if needed

from apps.api.app.services.orchestrator import orchestrator
from apps.api.app.services.commander import commander
from apps.api.app.services.mcp_server import mcp_server
from pydantic import BaseModel

class PlanRequest(BaseModel):
    prompt: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Antigravity API Starting...")
    await orchestrator.start()
    yield
    # Shutdown
    await orchestrator.stop()
    print("🛑 Antigravity API Stopping...")

app = FastAPI(title="Antigravity API", version="2.0.0", lifespan=lifespan)

# Mount Socket.IO app
app_socketio = socketio.ASGIApp(sio, app)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "online", "message": "Antigravity Orchestration API v2"}

@app.post("/api/v1/plan")
async def create_plan(request: PlanRequest):
    await commander.plan(request.prompt)
    return {"status": "planning_started"}

# MCP SSE Endpoints
sse = SseServerTransport("/mcp/messages")

@app.get("/mcp/sse")
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
        await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())

@app.post("/mcp/messages")
async def handle_messages(request: Request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit('message', {'data': 'Connected to Antigravity API'}, room=sid)

@sio.event
async def toggle_auto_trigger(sid, data):
    enabled = data.get("enabled", False)
    await blackboard.set_auto_trigger(enabled)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

def start():
    """Entry point for poetry/scripts"""
    uvicorn.run("apps.api.main:app_socketio", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()
