import tkinter as tk
from tkinter import ttk
from time import sleep
import threading
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)
sys.path.append(parent_directory)

from siyi_sdk import SIYISDK

# Initialize main window
window = tk.Tk()
window.title('SiYi Ground Control ( ͡❛ ͜ʖ ͡❛)')
window.geometry('320x240')

class CamAngle:
    def __init__(self):
        self.yaw = 0
        self.pitch = 0

    def addYaw(self, dy):
        self.yaw = max(min(self.yaw + dy, 45), -45)

    def addPitch(self, dp):
        self.pitch = max(min(self.pitch + dp, 25), -90)

    def zero(self):
        self.yaw = 0
        self.pitch = 0

cam_angle = CamAngle()
cam = SIYISDK(server_ip="192.168.144.25", port=37260)

# Connect to camera
if not cam.connect():
    print("❌ Failed to connect to camera.")
    exit(1)

cam.requestFollowMode()
sleep(3)  # allow time for attitude listener to initialize

# Verify attitude is being received
print("⏳ Waiting for attitude data...")
for _ in range(10):
    att = cam.getAttitude()
    print("Attitude:", att)
    if att and len(att) >= 2:
        break
    sleep(0.5)
else:
    print("⚠️ Attitude data not received. Gimbal movement may not work.")

# Lock for safe threading
lock = threading.Lock()

def move_gimbal():
    with lock:
        print(f"[MOVE] Yaw: {cam_angle.yaw}, Pitch: {cam_angle.pitch}")
        success = cam.setGimbalRotation(cam_angle.yaw, cam_angle.pitch)
        if not success:
            print("⚠️ Movement command failed (no attitude feedback)")

def threaded_move(update_func):
    def task():
        update_func()
        move_gimbal()
        att = cam.getAttitude()
        print("New Attitude:", att)
    threading.Thread(target=task).start()

# Button command functions
def pitch_up(): threaded_move(lambda: cam_angle.addPitch(5))
def pitch_down(): threaded_move(lambda: cam_angle.addPitch(-5))
def yaw_left(): threaded_move(lambda: cam_angle.addYaw(5))
def yaw_right(): threaded_move(lambda: cam_angle.addYaw(-5))
def center(): threaded_move(lambda: cam_angle.zero())

def zoom_in():
    def task():
        cam.requestZoomIn()
        sleep(0.5)
        cam.requestZoomHold()
        print("Zoom level:", cam.getZoomLevel())
    threading.Thread(target=task).start()

def zoom_out():
    def task():
        cam.requestZoomOut()
        sleep(0.5)
        cam.requestZoomHold()
        print("Zoom level:", cam.getZoomLevel())
    threading.Thread(target=task).start()

# Layout buttons
ttk.Button(window, text='🢁', command=pitch_up).grid(row=0, column=1, pady=2)
ttk.Button(window, text='🢃', command=pitch_down).grid(row=2, column=1, pady=2)
ttk.Button(window, text='🢀', command=yaw_left).grid(row=1, column=0, pady=2)
ttk.Button(window, text='🢂', command=yaw_right).grid(row=1, column=2, pady=2)
ttk.Button(window, text='🎯', command=center).grid(row=1, column=1, pady=2)
ttk.Button(window, text='🔎➕', command=zoom_in).grid(row=3, column=0, pady=2)
ttk.Button(window, text='🔎➖', command=zoom_out).grid(row=3, column=2, pady=2)

# Start GUI
window.mainloop()
cam.disconnect()
print("Exited cleanly.")


