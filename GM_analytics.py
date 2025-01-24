"""
Interfaces with GM detector via serial port,
providing CPM and microsievert measurements
real time as well as a post-capture summary

Author: Nicholas March
"""

# Imports
import serial
import tkinter as tk
from tkinter import StringVar
import threading
import numpy as np
import matplotlib.pyplot as plt
import time

# GUI Setup
root = tk.Tk()
root.title("Radiation Measurement")
root.geometry('400x300')  # Set the window size

# Styling
bg_color = 'light grey'
font_large = ('Helvetica', 14, 'bold')
root.configure(bg=bg_color)

# Variables for display
cpm_var = StringVar(value="Waiting for data...")
usv_hr_var = StringVar(value="")
usv_yr_var = StringVar(value="")
timer_var = StringVar(value="00:00:00")

# Data storage lists
times = []
cpms = []
errors = []

# Start time
start_time = time.time()

# Timer function
def tick():
    elapsed_time = time.time() - start_time
    timer_var.set(time.strftime('%H:%M:%S', time.gmtime(elapsed_time)))
    if running:
        root.after(1000, tick)  # update every second

# Function to update the GUI
def update_gui(val):
    elapsed_time = time.time() - start_time
    cpm = float(val)
    error = np.sqrt(cpm)
    usv_hr = cpm / 151.0
    usv_yr = usv_hr * 8766.0
    cpm_var.set(f"{cpm:.0f} CPM ± {error:.1f}")
    usv_hr_var.set(f"{usv_hr:.4f} µSv/hr ± {error/151.0:.4f}")
    usv_yr_var.set(f"{usv_yr:.4f} µSv/yr ± {(error/151.0)*8766.0:.4f}")
    times.append(elapsed_time)  # Append the current elapsed time
    cpms.append(cpm)
    errors.append(error)

# Display Labels
tk.Label(root, text="Elapsed Time:", bg=bg_color, font=font_large).pack()
timer_label = tk.Label(root, textvariable=timer_var, font=font_large, bg=bg_color)
timer_label.pack()

tk.Label(root, text="Counts per Minute:", bg=bg_color, font=font_large).pack()
cpm_label = tk.Label(root, textvariable=cpm_var, font=font_large, bg=bg_color)
cpm_label.pack()

tk.Label(root, text="Microsieverts per Hour:", bg=bg_color, font=font_large).pack()
usv_hr_label = tk.Label(root, textvariable=usv_hr_var, font=font_large, bg=bg_color)
usv_hr_label.pack()

tk.Label(root, text="Microsieverts per Year:", bg=bg_color, font=font_large).pack()
usv_yr_label = tk.Label(root, textvariable=usv_yr_var, font=font_large, bg=bg_color)
usv_yr_label.pack()

# Start/Stop handling
running = True

def toggle_running():
    global running
    running = not running
    if running:
        start_button.config(text="Pause")
        tick()  # Restart the ticking when resumed
        read_thread = threading.Thread(target=read_serial)
        read_thread.start()
    else:
        start_button.config(text="Resume")

def stop_reading():
    global running
    running = False
    start_button.config(text="Start")
    plot_data()

def plot_data():
    plt.errorbar(times, cpms, yerr=errors, fmt='o')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Counts per Minute (CPM)')
    plt.title('Radiation Count Over Time')
    plt.show()

# Thread function to handle serial port communication
def read_serial():
    try:
        with serial.Serial('COM7', 9600, timeout=1) as ser:
            print("Connected to device. Reading data...")
            while running:
                line = ser.readline()
                if line:
                    val = line.decode('utf-8').strip()
                    root.after(0, update_gui, val)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")

# Buttons
start_button = tk.Button(root, text="Pause", command=toggle_running, font=font_large)
start_button.pack(fill=tk.X)

stop_button = tk.Button(root, text="Stop", command=stop_reading, font=font_large)
stop_button.pack(fill=tk.X)

# Start the timer and data reading in separate threads
tick()
read_thread = threading.Thread(target=read_serial)
read_thread.start()

# Main GUI loop
root.mainloop()
