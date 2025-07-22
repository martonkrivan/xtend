import serial
import time

# SERIAL_PORT = "/dev/cu.usbmodem1101"  # Update as needed
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)


def send_command(cmd):
    print(f"Arduino: Sending '{cmd}'")
    ser.write((cmd + "\n").encode())
    response = ser.readline().decode().strip()
    print(f"Arduino: Received '{response}'")
    return response


def extend():
    return send_command("EXTEND")


def retract():
    return send_command("RETRACT")


def stop():
    return send_command("STOP")


def read_current():
    try:
        resp = send_command("READ")
        if resp.startswith("CURRENT:"):
            try:
                return int(resp.split(":")[1])
            except ValueError:
                print(f"Arduino: Invalid current value '{resp}'")
                return None
        else:
            print(f"Arduino: Unexpected response '{resp}'")
            return None
    except Exception as e:
        print(f"Arduino: Error reading current: {e}")
        return None


def to_amps(current_adc):
    voltage = (current_adc / 1023) * 5.0
    offset = voltage - 2.5
    return abs(offset / 0.066)


def lock_extend():
    return send_command("LOCK_EXTEND")


def lock_retract():
    return send_command("LOCK_RETRACT")


def stop_lock():
    return send_command("STOP_LOCK")


def close():
    ser.close()
