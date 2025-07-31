import os
import json
import time
import asyncio
from collections import deque
from bleak import BleakClient, BleakScanner

# 🔹 Address of Polar OH1+
DEVICE_ADDRESS = "A0:9E:1A:D7:25:0A"
HEART_RATE_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# 🔹 Path to JSON files
LAST_MEASUREMENT_FILE = "/tmp/heart_rate.json"
HISTORY_FILE = "/tmp/heart_rate_history.json"
DEVICE_STATUS_FILE = "/tmp/device_status.json"
TIME_ZERO_PULSE_FILE = "/tmp/time_zero_pulse.json"
BUTTON_ON_STATUS_FILE = "/tmp/button_on_status.json"

# 🔹 Length of the history
HISTORY_LENGTH = 300  # 5 minutes (300 sec)

# 🔹 Queue for storing history
heart_rate_history = deque(maxlen=HISTORY_LENGTH)

# Variables to track time when heart rate is 0
last_heart_rate = None  # Last recorded heart rate
last_timestamp = None  # Timestamp of last measurement
is_on_button_pressed = False  # Flag for tracking the "ON" button
zero_pulse_total_time = 0  # Total accumulated time when heart rate is 0


def read_button_status():
    """Reads the status of the ON button from a file."""
    global is_on_button_pressed
    if os.path.exists(BUTTON_ON_STATUS_FILE):
        try:
            with open(BUTTON_ON_STATUS_FILE, "r") as f:
                data = json.load(f)
                is_on_button_pressed = data.get("button_pressed", False)
        except json.JSONDecodeError:
            is_on_button_pressed = False
    else:
        is_on_button_pressed = False

def save_last_measurement(heart_rate):
    """Saves the last heart rate measurement to a JSON file."""
    global last_measurement_time
    timestamp = int(time.time())
    data = {"timestamp": timestamp, "heart_rate": heart_rate}
    last_measurement_time = timestamp  # Update last measurement time
    with open(LAST_MEASUREMENT_FILE, "w") as f:
        json.dump(data, f)

def save_history(heart_rate):
    """Updates the heart rate history file."""
    timestamp = int(time.time())
    entry = {"timestamp": timestamp, "heart_rate": heart_rate}
    heart_rate_history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(heart_rate_history), f)

def save_device_status(status):
    """Writes the device connection status to a file."""
    data = {"device_connected": status}
    with open(DEVICE_STATUS_FILE, "w") as f:
        json.dump(data, f)

def save_zero_pulse_time(time_elapsed):
    """Records the time elapsed since the pulse reached 0."""
    data = {"elapsed_time": time_elapsed}
    with open(TIME_ZERO_PULSE_FILE, "w") as f:
        json.dump(data, f)

def reset_zero_pulse_time():
    """Resets the heartbeat time to 0 when Django starts."""
    global zero_pulse_start_time
    zero_pulse_start_time = None
    with open(TIME_ZERO_PULSE_FILE, "w") as f:
        json.dump({"elapsed_time": 0}, f)

async def is_device_available(mac_address):
    """Checks if the device is available for connection."""
    print("🔎 Scanning for devices...")
    devices = await BleakScanner.discover()
    for device in devices:
        if device.address.upper() == mac_address.upper():
            print(f"✅ Device {mac_address} found, connecting!")
            return True
    print(f"❌ Device {mac_address} NOT found! Retrying in 5 sec...")
    return False

async def connect_to_device():
    """Main loop for handling the heart rate sensor."""
    global zero_pulse_start_time, last_measurement_time
    while True:
        try:
            # Check if the device is accessible before connecting
            available = await is_device_available(DEVICE_ADDRESS)
            if not available:
                save_device_status(False)
                await asyncio.sleep(5)
                continue

            async with BleakClient(DEVICE_ADDRESS) as client:
                save_device_status(True)
                print(f"🔗 Connected: {await client.is_connected()}")

                def handle_heart_rate_data(_, data):
                    """Processes heart rate data from the sensor."""
                    global zero_pulse_start_time, last_measurement_time
                    read_button_status()  # Read the button status from the file
                    heart_rate = data[1]
                    print(f"❤️ Pulse: {heart_rate} bpm")

                    # Save last measurement and history
                    save_last_measurement(heart_rate)
                    save_history(heart_rate)

                    # Read the previous accumulated time (if file exists)
                    accumulated_time = 0
                    if os.path.exists(TIME_ZERO_PULSE_FILE):
                        try:
                            with open(TIME_ZERO_PULSE_FILE, "r") as f:
                                data = json.load(f)
                                accumulated_time = data.get("elapsed_time", 0)
                        except json.JSONDecodeError:
                            accumulated_time = 0

                    print(f"⏱️ Previous accumulated time: {accumulated_time} sec")

                    if heart_rate == 0 and is_on_button_pressed:
                        if zero_pulse_start_time is None:
                            zero_pulse_start_time = time.time()
                            print("⚠️ Heart rate 0! Starting time tracking...")

                        # Update accumulated time in real-time
                        time_elapsed = time.time() - zero_pulse_start_time
                        total_time = accumulated_time + time_elapsed
                        save_zero_pulse_time(total_time)  # Save to file
                        print(f"⏱️ Updated time with heart rate 0: {total_time:.2f} sec.")

                    elif heart_rate != 0 and zero_pulse_start_time is not None:
                        # Final update before resetting timer
                        time_elapsed = time.time() - zero_pulse_start_time
                        accumulated_time += time_elapsed
                        save_zero_pulse_time(accumulated_time)
                        print(f"✅ Final saved accumulated time: {accumulated_time:.2f} sec.")

                        zero_pulse_start_time = None  # Reset timer

                    # Save time even if pulse is not 0 (needed for the front end)
                    else:
                        save_zero_pulse_time(accumulated_time)

                    if heart_rate == 0:
                        print("⚠️ Heart rate 0! Turning off the motor...")

                await client.start_notify(HEART_RATE_MEASUREMENT_UUID, handle_heart_rate_data)
                print("📡 Waiting for data...")

                while await client.is_connected():
                    await asyncio.sleep(1)

                print("⚠️ Connection lost! Reconnecting...")

        except Exception as e:
            save_device_status(False)  # We write the connection status to a file when an error occurs
            print(f"❌ Erroe: {e}")

        print("🔄 Trying to reconnect in 5 sec...")
        await asyncio.sleep(5)


# 🔥 Start the program
asyncio.run(connect_to_device())