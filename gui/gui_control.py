import tkinter as tk
from tkinter import ttk
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)
sys.path.append(parent_directory)

from siyi_sdk import SIYISDK

window = tk.Tk()
window.title('SiYi Ground Control')
window.geometry('320x240')

class CamAngle:
    def __init__(self, sdk):
        self.sdk = sdk
        self.update_from_device()

    def update_from_device(self):
        attitude = self.sdk.getAttitude()
        if attitude:
            self.yaw = attitude[0]
            self.pitch = attitude[1]
        else:
            self.yaw = 0
            self.pitch = 0
        print(f"[SYNC] Yaw: {self.yaw}, Pitch: {self.pitch}")

    def move(self, dyaw=0, dpitch=0):
        self.yaw += dyaw
        self.pitch += dpitch
        self.yaw = max(min(self.yaw, 45), -45)
        self.pitch = max(min(self.pitch, 25), -90)
        print(f"[MOVE] Yaw: {self.yaw}, Pitch: {self.pitch}")
        self.sdk.setGimbalRotation(self.yaw, self.pitch)

    def center(self):
        self.yaw = 0
        self.pitch = 0
        self.sdk.setGimbalRotation(0, 0)

# Init SDK
cam = SIYISDK(server_ip="192.168.144.25", port=37260)
if not cam.connect():
    print("Failed to connect")
    exit(1)

cam.requestFollowMode()
cam_angle = CamAngle(cam)

def pitch_up():
    cam_angle.move(dpitch=2)

def pitch_down():
    cam_angle.move(dpitch=-2)

def yaw_left():
    cam_angle.move(dyaw=2)

def yaw_right():
    cam_angle.move(dyaw=-2)

def pitch_yaw_center():
    cam_angle.center()

def zoom_in():
    cam.requestZoomIn()
    window.after(400, cam.requestZoomHold)
    print("Zoom in")

def zoom_out():
    cam.requestZoomOut()
    window.after(400, cam.requestZoomHold)
    print("Zoom out")

# GUI layout
ttk.Button(window, text='🢁', command=pitch_up).grid(row=0, column=1, pady=2)
ttk.Button(window, text='🢃', command=pitch_down).grid(row=2, column=1, pady=2)
ttk.Button(window, text='🢀', command=yaw_left).grid(row=1, column=0, pady=2)
ttk.Button(window, text='🢂', command=yaw_right).grid(row=1, column=2, pady=2)
ttk.Button(window, text='🎯', command=pitch_yaw_center).grid(row=1, column=1, pady=2)
ttk.Button(window, text='🔎➕', command=zoom_in).grid(row=3, column=0, pady=2)
ttk.Button(window, text='🔎➖', command=zoom_out).grid(row=3, column=2, pady=2)

window.mainloop()
cam.disconnect()
print("exit")
