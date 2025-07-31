
# Automatic Arterial Occlusion Device



This repository contains the code and documentation for the \*\*Automatic Arterial Occlusion Device\*\*, developed as a final projact biomedical engineering project at Afeka College.



The device is an \*\*automatic, motorized tourniquet\*\* designed to control severe arterial bleeding in emergency situations.  

It uses a \*\*Polar OH1 pulse sensor\*\* for real-time monitoring, a \*\*high‑torque worm‑geared servo motor\*\* for strap tightening, and a \*\*Raspberry Pi 4\*\* controller with a \*\*3.5" touchscreen interface\*\*.  

The system automatically stops tightening when no pulse is detected, ensuring safety and effective operation.



---



\## Features

\- \*\*Automatic pulse detection\*\* using the Polar OH1 (PPG + BLE).

\- \*\*Motorized strap tightening\*\* with a self‑locking worm‑geared servo.

\- \*\*Real‑time user interface\*\* via a 3.5" touchscreen.

\- \*\*Emergency stop\*\* and manual override option.

\- \*\*Portable, compact prototype\*\* with ~2 hours battery life.



---



\## Repository Structure

\- `en\_01` – Main program controlling the system (sensor reading + motor logic).

\- `pulse\_polar.py` – BLE communication with the Polar OH1 pulse sensor.

\- `motor\_control.py` – Motor control module for the tightening mechanism.

\- `display` – LCD screen drivers.

\- 'selenium' – Screen activation software.

\- `README.md` – Project description.



---



\## How to Use

1\. Turn on.

2\. Follow the on-screen instructions on the touchscreen to start/stop the device.



---



\## Authors

Bar Ahlavi \& Naor Fishman

Instructor: Eng. Eldan Gurevich

Afeka College of Engineering, Department of Medical Engineering





---



\## Notes

This project is a prototype for academic and research purposes.

It is not intended for immediate clinical use without further testing and regulatory approval.



