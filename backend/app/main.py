from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.state import State
from app.arduino import extend, retract, stop, read_current, to_amps, ping
import asyncio, time

# === CONFIGURABLE CONSTANTS ===
CUTOFF_MULTIPLIER = 2.0  # Used for both grace period and direction change
GRACE_PERIOD = 1.0  # seconds after startup or direction change
DISPLAY_INTERVAL = 0.5  # seconds for frontend updates
POLL_INTERVAL = 0.025  # seconds for current polling
WINDOW_SIZE = 2  # for smoothing current
PING_INTERVAL = 0.5  # seconds for Arduino watchdog

app = FastAPI()
state = State()
client = None
current_poll_task = None
startup_time = time.time()
run_cycle_task = None  # Track the background test task

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def poll_current_loop():
    global state, client
    current_window = []
    while True:
        current_adc = read_current()
        if current_adc is not None:
            current_amps = to_amps(current_adc)
            current_window.append(current_amps)
            if len(current_window) > WINDOW_SIZE:
                current_window.pop(0)
            smoothed_current = sum(current_window) / len(current_window)
            state.current = smoothed_current
            if client:
                await client.send_json(state.model_dump())
        await asyncio.sleep(0.1)


@app.on_event("startup")
async def start_current_poll():
    global current_poll_task
    if not current_poll_task:
        current_poll_task = asyncio.create_task(poll_current_loop())


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    global state, client, run_cycle_task
    client = ws
    await ws.accept()
    if client:
        await client.send_json(state.model_dump())

    try:
        while True:
            data = await ws.receive_json()
            match data.get("action"):
                case "start":
                    if run_cycle_task and not run_cycle_task.done():
                        # Prevent multiple tests at once
                        await ws.send_json({"error": "Test already running"})
                        continue
                    state = State()
                    state.status = "running"
                    state.total_cycles = data["total_cycles"]
                    state.actuate_time = data["actuate_time"]
                    state.rest_time = data["rest_time"]
                    state.current_cutoff = data["current_cutoff"]
                    state.cancel_requested = False
                    if client:
                        await client.send_json(state.model_dump())
                    run_cycle_task = asyncio.create_task(run_cycle())
                case "cancel":
                    state.cancel_requested = True
                    state.status = "failed"
                    state.phase = "idle"
                    state.phase_ends_at = 0.0
                    stop()
                    if run_cycle_task and not run_cycle_task.done():
                        run_cycle_task.cancel()
                    if client:
                        await client.send_json(state.model_dump())
                case "reset":
                    state = State()
                    state.cancel_requested = False
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


async def ping_watchdog():
    while True:
        try:
            ping()
        except Exception as e:
            print(f"Watchdog ping failed: {e}")
        await asyncio.sleep(PING_INTERVAL)


async def run_cycle():
    global state
    current_window = []
    last_display_update = 0
    cycle_start_time = time.time()
    ping_task = None
    for cycle in range(state.total_cycles):
        if state.cancel_requested:
            print("Cycle cancelled by user.")
            break
        state.current_cycle = cycle + 1
        print(f"Starting cycle {state.current_cycle}")
        state.phase = "actuating"
        state.phase_ends_at = time.time() + state.actuate_time * 60
        if client:
            await client.send_json(state.model_dump())
        actuate_end = time.time() + state.actuate_time * 60
        direction = "extend"  # Always start with extend
        last_direction = None
        # Start watchdog ping
        if ping_task is None or ping_task.done():
            ping_task = asyncio.create_task(ping_watchdog())
        while time.time() < actuate_end:
            if state.cancel_requested:
                print("Actuation cancelled by user.")
                break
            # Set up for this direction
            direction_changed = last_direction != direction
            phase_start = time.time()
            if direction == "extend":
                print("Sending EXTEND command")
                extend()
            else:
                print("Sending RETRACT command")
                retract()
            last_direction = direction
            # Run actuator in this direction until cutoff or actuate_end
            await actuator_phase(
                actuate_end,
                current_window,
                last_display_update,
                direction_changed,
                phase_start,
                cycle_start_time,
                phase_name=direction.upper(),
            )
            stop()
            await asyncio.sleep(0.5)
            # Alternate direction
            direction = "retract" if direction == "extend" else "extend"
        # Stop watchdog ping during rest
        if ping_task and not ping_task.done():
            ping_task.cancel()
            try:
                await ping_task
            except Exception:
                pass
        if state.cancel_requested:
            print("Cycle cancelled during rest phase.")
            break
        # --- REST ---
        if state.current_cycle < state.total_cycles:
            state.phase = "resting"
            state.phase_ends_at = time.time() + state.rest_time * 60
            if client:
                await client.send_json(state.model_dump())
            await asyncio.sleep(state.rest_time * 60)
    # Ensure ping is stopped at end
    if ping_task and not ping_task.done():
        ping_task.cancel()
        try:
            await ping_task
        except Exception:
            pass
    state.status = "completed" if not state.cancel_requested else "failed"
    state.phase = "idle"
    state.phase_ends_at = 0.0
    if client:
        await client.send_json(state.model_dump())


def get_cutoff(now, phase_start, cycle_start, direction_changed):
    # Only apply multiplier after switching directions, not at cycle start
    if direction_changed and (now - phase_start) < GRACE_PERIOD:
        return state.current_cutoff * CUTOFF_MULTIPLIER
    return state.current_cutoff


async def actuator_phase(
    actuate_end,
    current_window,
    last_display_update,
    direction_changed,
    phase_start,
    cycle_start,
    phase_name="ACTUATE",
):
    global state, client
    while time.time() < actuate_end:
        if state.cancel_requested:
            print(f"{phase_name} cancelled by user.")
            break
        # Use the smoothed value from state.current
        now = time.time()
        if now - last_display_update >= DISPLAY_INTERVAL:
            if client:
                await client.send_json(state.model_dump())
            last_display_update = now
        cutoff = get_cutoff(now, phase_start, cycle_start, direction_changed)
        print(f"{phase_name} - Current: {state.current:.2f} A, Cutoff: {cutoff:.2f} A")
        if state.current >= cutoff:
            print(f"Current cutoff reached during {phase_name}")
            break
        await asyncio.sleep(POLL_INTERVAL)
