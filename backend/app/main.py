from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.state import State
from app.arduino import *
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
                case "manual_extend":
                    extend()
                case "manual_retract":
                    retract()
                case "manual_stop":
                    stop()
    except WebSocketDisconnect:
        if client is ws:
            client = None


async def start_test():
    global state
    try:
        current_window = []
        window_size = 2
        display_interval = 0.5  # 500ms
        last_display_update = 0
        last_direction = None  # 'extend' or 'retract'
        grace_period = 0.2  # 200ms
        grace_multiplier = 1.2
        while state.current_cycle < state.total_cycles:
            state.current_cycle += 1
            print(f"Starting cycle {state.current_cycle}")
            state.phase = "actuating"
            state.phase_ends_at = time.time() + state.actuate_time * 60
            if client:
                await client.send_json(state.model_dump())

            actuate_end = time.time() + state.actuate_time * 60
            # --- EXTEND ---
            print("Sending EXTEND command")
            extend()
            direction_changed = last_direction != "extend"
            last_direction = "extend"
            extend_start = time.time()
            while time.time() < actuate_end:
                current_adc = read_current()
                if current_adc is not None:
                    current_amps = to_amps(current_adc)
                    current_window.append(current_amps)
                    if len(current_window) > window_size:
                        current_window.pop(0)
                    smoothed_current = sum(current_window) / len(current_window)
                    # Only update frontend every 500ms
                    now = time.time()
                    if now - last_display_update >= display_interval:
                        state.current = smoothed_current
                        if client:
                            await client.send_json(state.model_dump())
                        last_display_update = now
                    # Grace period logic
                    if direction_changed and (now - extend_start < grace_period):
                        cutoff = state.current_cutoff * grace_multiplier
                    else:
                        cutoff = state.current_cutoff
                    print(
                        f"Extending - Raw ADC: {current_adc}, Current: {current_amps:.2f} A, Smoothed: {smoothed_current:.2f} A, Cutoff: {cutoff:.2f} A"
                    )
                    if current_amps >= cutoff:
                        print("Current cutoff reached during EXTEND")
                        break
                await asyncio.sleep(0.025)
            stop()
            await asyncio.sleep(0.5)

            # --- RETRACT ---
            print("Sending RETRACT command")
            retract()
            direction_changed = last_direction != "retract"
            last_direction = "retract"
            retract_start = time.time()
            while time.time() < actuate_end:
                current_adc = read_current()
                if current_adc is not None:
                    current_amps = to_amps(current_adc)
                    current_window.append(current_amps)
                    if len(current_window) > window_size:
                        current_window.pop(0)
                    smoothed_current = sum(current_window) / len(current_window)
                    # Only update frontend every 500ms
                    now = time.time()
                    if now - last_display_update >= display_interval:
                        state.current = smoothed_current
                        if client:
                            await client.send_json(state.model_dump())
                        last_display_update = now
                    # Grace period logic
                    if direction_changed and (now - retract_start < grace_period):
                        cutoff = state.current_cutoff * grace_multiplier
                    else:
                        cutoff = state.current_cutoff
                    print(
                        f"Retracting - Raw ADC: {current_adc}, Current: {current_amps:.2f} A, Smoothed: {smoothed_current:.2f} A, Cutoff: {cutoff:.2f} A"
                    )
                    if current_amps >= cutoff:
                        print("Current cutoff reached during RETRACT")
                        break
                await asyncio.sleep(0.025)
            stop()
            await asyncio.sleep(0.5)

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
        print("Test cancelled")
        stop()
        if client:
            await client.send_json(state.model_dump())


def to_amps(current_adc):
    voltage = (current_adc / 1023) * 5.0
    offset = voltage - 2.5
    return abs(offset / 0.066)
