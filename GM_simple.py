"""
Interfaces with GM detector via serial port,
providing CPM and microsievert measurements
real time as well as a post-capture summary

Author: Nicholas March
"""

# Imports
import serial

# Port Configuration
serial_port = 'COM7'
baud_rate = 9600

# Particle Detection
try:
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        print("Connected to device. Reading data...")
        while True:
            line = ser.readline()
            if line:
                val = line.decode('utf-8').strip()
                print("{:<3} CPM | {:>7.4f} \u03BCSv/hr | {:>7.4f} \u03BCSv/yr".format(val,(float(val)/151.0), ((float(val)/151.0)*8766.0)))

# Error Handling
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
except KeyboardInterrupt:
    print("Program exited by user.")
