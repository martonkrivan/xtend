from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.state import State
import asyncio, time

app = FastAPI()
state = State()
client = None
task = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    global state, client, task
    client = ws
    await ws.accept()
    if client:
        await client.send_json(state.model_dump())

    try:
        while True:
            data = await ws.receive_json()
            match data.get("action"):
                case "start":
                    state = State()
                    state.status = "running"
                    state.total_cycles = data["total_cycles"]
                    state.actuate_time = data["actuate_time"]
                    state.rest_time = data["rest_time"]
                    state.current_cutoff = data["current_cutoff"]
                    if client:
                        await client.send_json(state.model_dump())
                    if not task or task.done():
                        task = asyncio.create_task(start_test())
                case "cancel":
                    if task:
                        task.cancel()
                        task = None
                        state.status = "failed"
                        state.phase = "idle"
                        state.phase_ends_at = 0.0
                    if client:
                        await client.send_json(state.model_dump())
                case "reset":
                    state = State()
                    if client:
                        await client.send_json(state.model_dump())
    except WebSocketDisconnect:
        if client is ws:
            client = None


async def start_test():
    global state
    try:
        while state.current_cycle < state.total_cycles:
            state.current_cycle += 1
            state.phase = "actuating"
            state.phase_ends_at = time.time() + state.actuate_time * 60
            if client:
                await client.send_json(state.model_dump())
            await asyncio.sleep(state.actuate_time * 60)

            if state.current_cycle < state.total_cycles:
                state.phase = "resting"
                state.phase_ends_at = time.time() + state.rest_time * 60
                if client:
                    await client.send_json(state.model_dump())
                await asyncio.sleep(state.rest_time * 60)

        state.status = "completed"
        state.phase = "idle"
        state.phase_ends_at = 0.0
        if client:
            await client.send_json(state.model_dump())

    except asyncio.CancelledError:
        if client:
            await client.send_json(state.model_dump())
