import tkinter as tk
from tkinter import ttk
import sys
import os
import threading

current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)
sys.path.append(parent_directory)

from siyi_sdk import SIYISDK

# Create window
window = tk.Tk()
window.title('SiYi Ground Control')
window.geometry('320x240')

# Connect to SIYI SDK
cam = SIYISDK(server_ip="192.168.144.25", port=37260)
if not cam.connect():
    print("Connection failed")
    exit(1)

cam.requestFollowMode()

# Camera angle state
class CamAngle:
    def __init__(self, sdk):
        self.sdk = sdk
        self.lock = threading.Lock()
        att = sdk.getAttitude()
        self.yaw = att[0] if att else 0
        self.pitch = att[1] if att else 0

    def move(self, dyaw=0, dpitch=0):
        def _move():
            with self.lock:
                self.yaw += dyaw
                self.pitch += dpitch
                self.yaw = max(min(self.yaw, 45), -45)
                self.pitch = max(min(self.pitch, 25), -90)
                print(f"[MOVE] Yaw: {self.yaw}, Pitch: {self.pitch}")
                self.sdk.setGimbalRotation(self.yaw, self.pitch)
        threading.Thread(target=_move).start()

    def center(self):
        def _center():
            with self.lock:
                self.yaw = 0
                self.pitch = 0
                self.sdk.setGimbalRotation(0, 0)
        threading.Thread(target=_center).start()

    def zoom_in(self):
        def _zoom():
            self.sdk.requestZoomIn()
            self.sdk.requestZoomHold()
        threading.Thread(target=_zoom).start()

    def zoom_out(self):
        def _zoom():
            self.sdk.requestZoomOut()
            self.sdk.requestZoomHold()
        threading.Thread(target=_zoom).start()

cam_angle = CamAngle(cam)

# Button callbacks
def pitch_up(): cam_angle.move(dpitch=2)
def pitch_down(): cam_angle.move(dpitch=-2)
def yaw_left(): cam_angle.move(dyaw=2)
def yaw_right(): cam_angle.move(dyaw=-2)
def pitch_yaw_center(): cam_angle.center()
def zoom_in(): cam_angle.zoom_in()
def zoom_out(): cam_angle.zoom_out()

# GUI Layout
ttk.Button(window, text='🢁', command=pitch_up).grid(row=0, column=1, pady=2)
ttk.Button(window, text='🢃', command=pitch_down).grid(row=2, column=1, pady=2)
ttk.Button(window, text='🢀', command=yaw_left).grid(row=1, column=0, pady=2)
ttk.Button(window, text='🢂', command=yaw_right).grid(row=1, column=2, pady=2)
ttk.Button(window, text='🎯', command=pitch_yaw_center).grid(row=1, column=1, pady=2)
ttk.Button(window, text='🔎➕', command=zoom_in).grid(row=3, column=0, pady=2)
ttk.Button(window, text='🔎➖', command=zoom_out).grid(row=3, column=2, pady=2)

# Run GUI
window.mainloop()
cam.disconnect()
print("exit")

