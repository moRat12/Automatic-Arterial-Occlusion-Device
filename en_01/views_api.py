# ! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
from django.http import JsonResponse
from .motor_control import get_motor_status

# 🔹 File paths
HISTORY_FILE = "/tmp/heart_rate_history.json"
LAST_MEASUREMENT_FILE = "/tmp/heart_rate.json"
DEVICE_STATUS_FILE = "/tmp/device_status.json"
MOTOR_STATUS_FILE = "/tmp/motor_status.json"
TIME_ZERO_PULSE_FILE = "/tmp/time_zero_pulse.json"

# 🔹 Global variables
zero_pulse_time = 0  # Accumulated zero pulse time

# Function to load zero pulse time from file
def load_zero_pulse_time():
    global zero_pulse_time
    try:
        with open(TIME_ZERO_PULSE_FILE, "r") as f:
            data = json.load(f)
            zero_pulse_time = data.get("elapsed_time", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        zero_pulse_time = 0

# Load saved data on startup
load_zero_pulse_time()

# 🔥 API: Get heart rate history (including zero pulse time)
def get_heart_rate_history(request):
    print("📊 Fetching heart rate history...")

    try:
        # Read heart rate history
        try:
            with open(HISTORY_FILE, "r") as file:
                history_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            history_data = []
            print("⚠️ History file not found or corrupted.")

        # Read last measurement
        try:
            with open(LAST_MEASUREMENT_FILE, "r") as file:
                last_measurement = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            last_measurement = {"heart_rate": 0}
            print("⚠️ Last measurement file not found or corrupted.")

        # Update zero pulse time before sending response
        load_zero_pulse_time()

        # Limit history to last 50 values
        last_50_values = history_data[-50:] if len(history_data) > 50 else history_data

        # Get sensor and motor status
        m_pulse_sensor_status = get_device_status()
        m_motor_status = get_motor_status()

        # Return JSON with history and last measurement
        response_data = {
            "history": last_50_values,
            "last_measurement": last_measurement,
            "pulse_sensor_available": m_pulse_sensor_status,
            "motor_on": m_motor_status,
            "zero_pulse_time": zero_pulse_time
        }
        print("📡 Sending response:", response_data)
        return JsonResponse(response_data, safe=False)

    except Exception as e:
        print("❌ Error:", e)
        return JsonResponse({"error": str(e)}, status=500)

# 🔥 API: Get device status
def get_device_status():
    """Check device connection status."""
    try:
        with open(DEVICE_STATUS_FILE, "r") as file:
            status = json.load(file).get("device_connected", False)
    except Exception as e:
        print(f"❌ Device status error: {e}")
        status = False
    return status