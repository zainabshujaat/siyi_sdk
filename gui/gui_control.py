import tkinter as tk
from tkinter import ttk
from time import sleep
import threading
import sys
import os

# Adjust paths
current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)
sys.path.append(parent_directory)

from siyi_sdk import SIYISDK

# Window setup
window = tk.Tk()
window.title('SiYi Ground Control ( ͡❛ ͜ʖ ͡❛)')
window.geometry('320x240')

# Gimbal angle controller
class CamAngle:
    def __init__(self):
        self.yaw = 0
        self.pitch = 0

    def addYaw(self, dy):
        self.yaw += dy
        self.yaw = max(min(self.yaw, 45), -45)

    def addPitch(self, dp):
        self.pitch += dp
        self.pitch = max(min(self.pitch, 25), -90)

    def zeroYaw(self):
        self.yaw = 0

    def zeroPitch(self):
        self.pitch = 0

cam_angle = CamAngle()

# Connect to gimbal
cam = SIYISDK(server_ip="192.168.144.25", port=37260)
if not cam.connect():
    print("No connection")
    exit(1)

cam.requestFollowMode()
print("⏳ Waiting for attitude data...")
sleep(1)
print("Attitude:", cam.getAttitude())

# Lock for thread-safe access
lock = threading.Lock()

# Non-blocking gimbal movement
def move_gimbal():
    with lock:
        print(f"[MOVE] Yaw: {cam_angle.yaw}, Pitch: {cam_angle.pitch}")
        cam.sendGimbalRotationCommand(cam_angle.yaw, cam_angle.pitch)

# Button commands
def pitch_up():
    cam_angle.addPitch(5)
    threading.Thread(target=move_gimbal).start()

def pitch_down():
    cam_angle.addPitch(-5)
    threading.Thread(target=move_gimbal).start()

def yaw_left():
    cam_angle.addYaw(5)
    threading.Thread(target=move_gimbal).start()

def yaw_right():
    cam_angle.addYaw(-5)
    threading.Thread(target=move_gimbal).start()

def pitch_yaw_center():
    cam_angle.zeroYaw()
    cam_angle.zeroPitch()
    threading.Thread(target=move_gimbal).start()

def zoom_in():
    def zoom_task():
        cam.requestZoomIn()
        sleep(0.5)
        cam.requestZoomHold()
        print("Zoom level:", cam.getZoomLevel())
    threading.Thread(target=zoom_task).start()

def zoom_out():
    def zoom_task():
        cam.requestZoomOut()
        sleep(0.5)
        cam.requestZoomHold()
        print("Zoom level:", cam.getZoomLevel())
    threading.Thread(target=zoom_task).start()

# Layout
ttk.Button(window, text='🢁', command=pitch_up).grid(row=0, column=1, pady=2)
ttk.Button(window, text='🢃', command=pitch_down).grid(row=2, column=1, pady=2)
ttk.Button(window, text='🢀', command=yaw_left).grid(row=1, column=0, pady=2)
ttk.Button(window, text='🢂', command=yaw_right).grid(row=1, column=2, pady=2)
ttk.Button(window, text='🎯', command=pitch_yaw_center).grid(row=1, column=1, pady=2)
ttk.Button(window, text='🔎➕', command=zoom_in).grid(row=3, column=0, pady=2)
ttk.Button(window, text='🔎➖', command=zoom_out).grid(row=3, column=2, pady=2)

# Run GUI loop
window.mainloop()
cam.disconnect()
print("exit")

