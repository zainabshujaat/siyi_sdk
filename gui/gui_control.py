import tkinter as tk
from tkinter import ttk
import threading
from time import sleep
import sys
import os

# Fix Python path to import SIYISDK
current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)
sys.path.append(parent_directory)

from siyi_sdk import SIYISDK  # <-- ADD THIS IMPORT

# Global camera object
cam = None

class CamAngle:
    def __init__(self):
        self.yaw = 0
        self.pitch = 0

    def addYaw(self, dy):
        self.yaw += dy
        self.yaw = max(-45, min(45, self.yaw))  # Clamp between -45 and 45

    def addPitch(self, dp):
        self.pitch += dp
        self.pitch = max(-90, min(25, self.pitch))  # Clamp between -90 and 25

    def zeroYaw(self):
        self.yaw = 0

    def zeroPitch(self):
        self.pitch = 0

cam_angle = CamAngle()

# Initialize SIYI SDK (run in a separate thread)
def init_cam():
    global cam  # Declare `cam` as global
    cam = SIYISDK(server_ip="192.168.144.25", port=37260)
    if not cam.connect():
        print("No connection")
        exit(1)
    cam.requestFollowMode()

# Run SDK commands in a thread to avoid freezing GUI
def send_gimbal_command():
    if cam:  # Only run if `cam` exists
        cam.setGimbalRotation(cam_angle.yaw, cam_angle.pitch)
        print("Attitude:", cam.getAttitude())

def pitch_up():
    cam_angle.addPitch(5)
    threading.Thread(target=send_gimbal_command, daemon=True).start()

def pitch_down():
    cam_angle.addPitch(-5)
    threading.Thread(target=send_gimbal_command, daemon=True).start()

def yaw_left():
    cam_angle.addYaw(5)
    threading.Thread(target=send_gimbal_command, daemon=True).start()

def yaw_right():
    cam_angle.addYaw(-5)
    threading.Thread(target=send_gimbal_command, daemon=True).start()

def picth_yaw_center():
    cam_angle.zeroYaw()
    cam_angle.zeroPitch()
    threading.Thread(target=send_gimbal_command, daemon=True).start()

def zoom_in():
    def _zoom_in():
        if cam:
            cam.requestZoomIn()
            sleep(0.5)
            cam.requestZoomHold()
            sleep(0.5)
            print("Zoom level:", cam.getZoomLevel())
    threading.Thread(target=_zoom_in, daemon=True).start()

def zoom_out():
    def _zoom_out():
        if cam:
            cam.requestZoomOut()
            sleep(0.5)
            cam.requestZoomHold()
            sleep(0.5)
            print("Zoom level:", cam.getZoomLevel())
    threading.Thread(target=_zoom_out, daemon=True).start()

# Initialize camera in a thread
threading.Thread(target=init_cam, daemon=True).start()

# GUI Setup
window = tk.Tk()
window.title('SiYi Ground Control ( ͡❛ ͜ʖ ͡❛)')
window.geometry('320x240')

# Buttons
pitch_up_button = ttk.Button(window, text='🢁', command=pitch_up)
pitch_down_button = ttk.Button(window, text='🢃', command=pitch_down)
yaw_left_button = ttk.Button(window, text='🢀', command=yaw_left)
yaw_right_button = ttk.Button(window, text='🢂', command=yaw_right)
center_button = ttk.Button(window, text='🎯', command=picth_yaw_center)
zoom_in_button = ttk.Button(window, text='🔎➕', command=zoom_in)
zoom_out_button = ttk.Button(window, text='🔎➖', command=zoom_out)

# Grid Layout
pitch_up_button.grid(row=0, column=1, pady=2)
pitch_down_button.grid(row=2, column=1, pady=2)
yaw_left_button.grid(row=1, column=0, pady=2)
yaw_right_button.grid(row=1, column=2, pady=2)
center_button.grid(row=1, column=1, pady=2)
zoom_in_button.grid(row=3, column=0, pady=2)
zoom_out_button.grid(row=3, column=2, pady=2)

# Run GUI
window.mainloop()

# Disconnect safely (only if `cam` exists)
if cam:
    cam.disconnect()
print("exit")
