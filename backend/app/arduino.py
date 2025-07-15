import os
import serial
import time

serial_port = os.getenv("ARDUINO_PORT")
ser = serial.Serial(serial_port, 9600, timeout=1)
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


def close():
    ser.close()
