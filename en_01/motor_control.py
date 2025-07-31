# ! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import RPi.GPIO as GPIO
import threading
import time
import os

MOTOR_PIN = 19
HISTORY_FILE = "/tmp/heart_rate.json"
MOTOR_STATUS_FILE = "/tmp/motor_status.json"
BUTTON_ON_STATUS_FILE = "/tmp/button_on_status.json"
LAST_BUTTON_PRESSED_FILE = "/tmp/last_button_pressed.json"

motor_running = False  # Motor Status Flag
lock = threading.Lock()  # Lock for sync
motor_timer = None  # Motor Shutdown Timer

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN, GPIO.OUT)
GPIO.output(MOTOR_PIN, GPIO.LOW)  # Ensure motor is off at startup


def reset_motor_status():
    """Resetting the motor state at start"""
    global motor_running
    with lock:
        motor_running = False
        GPIO.output(MOTOR_PIN, GPIO.LOW)
    print("Motor status reset to OFF")


def get_last_heart_rate():
    """Gets the latest heart rate measurement from a file"""
    if not os.path.exists(HISTORY_FILE):
        return None
    try:
        with open(HISTORY_FILE, "r") as file:
            data = json.load(file)
            return data.get("heart_rate")
    except Exception as e:
        print("Error reading pulse file:", e)
        return None


def get_button_on_status():
    """Checks if the 'ON' button was pressed at least once."""
    if not os.path.exists(BUTTON_ON_STATUS_FILE):
        return False
    try:
        with open(BUTTON_ON_STATUS_FILE, "r") as file:
            data = json.load(file)
            return data.get("button_pressed", False)
    except Exception as e:
        print("Error reading button status file:", e)
        return False


def get_last_button_pressed():
    """Gets the last pressed button ('ON' or 'OFF')."""
    if not os.path.exists(LAST_BUTTON_PRESSED_FILE):
        return None
    try:
        with open(LAST_BUTTON_PRESSED_FILE, "r") as file:
            data = json.load(file)
            return data.get("last_button")
    except Exception as e:
        print("Error reading last button file:", e)
        return None


def set_last_button_pressed(button):
    print("set_last_button_pressed  set_last_button_pressed  set_last_button_pressed  set_last_button_pressed")
    """Sets the last pressed button."""
    try:
        with open(LAST_BUTTON_PRESSED_FILE, "w") as file:
            json.dump({"last_button": button}, file)
    except Exception as e:
        print("Error writing last button file:", e)


def pulse_monitor():
    """Monitors the pulse and stops the motor if it reaches 0, restarts if it goes above 0."""
    global motor_running
    while True:
        heart_rate = get_last_heart_rate()
        print("heart_rate = ", heart_rate)
        print(" 1=", get_button_on_status())  ## false
        print(" 2=", get_last_button_pressed())  ## off
        print(" 3=", motor_running)  ## false

        if heart_rate == 0:
            print("Pulse 0! Stopping the motor.")
            turn_off_motor()
        elif heart_rate is not None and heart_rate > 0:
            # Check if the motor can be restarted
            if get_button_on_status() and get_last_button_pressed() == "ON" and not motor_running:
                print("Pulse restored! Restarting motor.")
                turn_on_motor()
        time.sleep(5)


def turn_on_motor():
    """Turning on the motor (no more than 60 seconds, turns off when the pulse is 0)"""
    global motor_running, motor_timer
    with lock:
        motor_running = True
        GPIO.output(MOTOR_PIN, GPIO.HIGH)
        print("Motor ON")
        motor_timer = threading.Timer(60, turn_off_motor)
        motor_timer.start()

        try:
            with open(MOTOR_STATUS_FILE, "w") as f:
                json.dump({"motor_running": True}, f)
        except Exception as e:
            print(f"Error writing to {MOTOR_STATUS_FILE}: {e}")

        try:
            with open(BUTTON_ON_STATUS_FILE, "w") as f:
                json.dump({"button_pressed": True}, f)
        except Exception as e:
            print(f"Error writing to {BUTTON_ON_STATUS_FILE}: {e}")

        # set_last_button_pressed("ON")
        print("🔄 Button ON pressed")
    return "Motor ON"


def turn_off_motor():
    """Stops the motor and cancels all timers"""
    global motor_running, motor_timer
    with lock:
        GPIO.output(MOTOR_PIN, GPIO.LOW)
        motor_running = False
        print("Motor OFF")
        if motor_timer:
            motor_timer.cancel()
            motor_timer = None
        try:
            with open(MOTOR_STATUS_FILE, "w") as f:
                json.dump({"motor_running": False}, f)
        except Exception as e:
            print(f"Error writing to {MOTOR_STATUS_FILE}: {e}")
        # set_last_button_pressed("OFF")
    return "Motor OFF"


def get_motor_status():
    """Returns the current state of the motor"""
    return GPIO.input(MOTOR_PIN) == GPIO.HIGH


def cleanup():
    """Clears GPIO before exiting"""
    GPIO.cleanup()
    print("GPIO cleanup done.")


import atexit

atexit.register(cleanup)

# Start pulse monitoring in a separate thread
pulse_thread = threading.Thread(target=pulse_monitor, daemon=True)
pulse_thread.start()
