import serial
import os
import sys
import time
import numpy as np
from scipy.spatial.transform import Rotation as R_sci
from vedo import Mesh, Plotter, Text2D

# --- CONFIG ---
SERIAL_PORT = 'COM3' 
BAUD_RATE = 115200
FILENAME = "SUMEC_Mk5_Pro.stl"
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_PATH, FILENAME)
UPDATE_INTERVAL = 0.05

# --- GLOBALS ---
quat_offset = R_sci.from_quat([0.0, 0.0, 0.0, 1.0]) 
current_quat = R_sci.from_quat([0.0, 0.0, 0.0, 1.0])
last_update = 0.0

# --- SERIAL SETUP ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    ser.setDTR(True)
    ser.setRTS(True)
except Exception as e:
    print(f"Serial Error: {e}")
    sys.exit()

# --- VEDO SETUP ---
plt = Plotter(axes=1, bg='white', size=(1000, 700), interactive=False)

if not os.path.exists(MODEL_PATH):
    print(f"ERROR: {FILENAME} not found at {MODEL_PATH}")
    sys.exit()

model = Mesh(MODEL_PATH).c('gold')
original_pts = model.vertices.copy()

try:
    model.add_shadow()
except Exception:
    pass

msg = Text2D("Initializing...", pos='top-left', c='black', font='VictorMono')

# --- KEYBOARD CALLBACK ---
def on_key(event):
    global quat_offset, current_quat
    if event.keypress in ('z', 'Z'):
        quat_offset = current_quat
        print("\n>>> SENSOR ZEROED <<<\n")

# --- TIMER CALLBACK ---
def loop_func(event):
    global current_quat, last_update

    now = time.time()
    latest_line = None
    
    try:
        while ser.in_waiting > 0:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if "Quat:" in line:
                latest_line = line
    except Exception:
        pass

    if latest_line:
        try:
            # Expected Arduino output: "Quat: w, x, y, z"
            payload = latest_line.split(":")[1].split(",")
            w, x, y, z = [float(p.strip()) for p in payload]
            
            # OUTPUT TO TERMINAL
            print(f"QUAT DATA -> W: {w:+.4f} X: {x:+.4f} Y: {y:+.4f} Z: {z:+.4f}")
            sys.stdout.flush() 

            # scipy expects [x, y, z, w]
            current_quat = R_sci.from_quat([-y, z, -x, w])
        except Exception as e:
            print(f"Parse error: {e}")

    if now - last_update < UPDATE_INTERVAL:
        return
    last_update = now

    # Relative rotation calculation
    relative_quat = quat_offset.inv() * current_quat

    # Apply rotation matrix to model
    R = relative_quat.as_matrix()
    model.vertices = (R @ original_pts.T).T

    # Calculate Euler for UI display
    euler_display = relative_quat.as_euler('xyz', degrees=True)
    roll, pitch, yaw = euler_display

    new_info = (f" LIVE DATA (Press 'z' to Zero)\n"
                f" Roll:  {roll:+.2f}°\n"
                f" Pitch: {pitch:+.2f}°\n"
                f" Yaw:   {yaw:+.2f}°")
    msg.text(new_info)
    plt.render()

# --- REGISTER CALLBACKS & LAUNCH ---
plt.add_callback('key press', on_key)
plt.add_callback('timer', loop_func)
plt.timer_callback('start', dt=10)
plt.show(model, msg, interactive=True)