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
    except WebSocketDisconnect:
        if client is ws:
            client = None


async def start_test():
    global state
    try:
        while state.current_cycle < state.total_cycles:
            state.current_cycle += 1
            print(f"Starting cycle {state.current_cycle}")
            state.phase = "actuating"
            state.phase_ends_at = time.time() + state.actuate_time * 60
            if client:
                await client.send_json(state.model_dump())

            actuate_end = time.time() + state.actuate_time * 60
            while time.time() < actuate_end:
                # Extend until current_cutoff or time is up
                print("Sending EXTEND command")
                extend()
                while time.time() < actuate_end:
                    current_adc = read_current()
                    if current_adc is not None:
                        current_amps = to_amps(current_adc)
                        print(
                            f"Extending - Raw ADC: {current_adc}, Current: {current_amps:.2f} A"
                        )
                        if current_amps >= state.current_cutoff:
                            print("Current cutoff reached during EXTEND")
                            break
                    await asyncio.sleep(0.1)
                stop()
                await asyncio.sleep(0.5)

                # Retract until current_cutoff or time is up
                print("Sending RETRACT command")
                retract()
                while time.time() < actuate_end:
                    current_adc = read_current()
                    if current_adc is not None:
                        current_amps = to_amps(current_adc)
                        print(
                            f"Retracting - Raw ADC: {current_adc}, Current: {current_amps:.2f} A"
                        )
                        if current_amps >= state.current_cutoff:
                            print("Current cutoff reached during RETRACT")
                            break
                    await asyncio.sleep(0.1)
                stop()
                await asyncio.sleep(0.5)

            # After actuating, always retract until current_cutoff is reached
            print("Final retract to ensure fully retracted position")
            timeout = 10  # seconds
            start_time = time.time()
            retract()
            while time.time() - start_time < timeout:
                current_adc = read_current()
                if current_adc is not None:
                    current_amps = to_amps(current_adc)
                    print(
                        f"Final Retract - Raw ADC: {current_adc}, Current: {current_amps:.2f} A"
                    )
                    if current_amps >= state.current_cutoff:
                        print("Current cutoff reached during final retract")
                        break
                await asyncio.sleep(0.1)
            stop()

            if state.current_cycle < state.total_cycles:
                state.phase = "resting"
                state.phase_ends_at = time.time() + state.rest_time * 60
                if client:
                    await client.send_json(state.model_dump())
                # Ensure actuator is retracted before resting
                print("Ensuring actuator is retracted before resting")
                retract()
                for _ in range(100):  # up to 10 seconds
                    current_adc = read_current()
                    if current_adc is not None:
                        current_amps = to_amps(current_adc)
                        print(
                            f"Rest Retract - Raw ADC: {current_adc}, Current: {current_amps:.2f} A"
                        )
                        if current_amps >= state.current_cutoff:
                            print("Current cutoff reached during rest retract")
                            break
                    await asyncio.sleep(0.1)
                stop()
                await asyncio.sleep(state.rest_time * 60)

        state.status = "completed"
        state.phase = "idle"
        state.phase_ends_at = 0.0
        if client:
            await client.send_json(state.model_dump())

    except asyncio.CancelledError:
        print("Test cancelled")
        stop()
        close()
        if client:
            await client.send_json(state.model_dump())
    close()


def to_amps(current_adc):
    voltage = (current_adc / 1023) * 5.0
    offset = voltage - 2.5
    return abs(offset / 0.066)
