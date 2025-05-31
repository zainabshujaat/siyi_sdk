import tkinter as tk
from tkinter import ttk
from time import sleep
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)
sys.path.append(parent_directory)

from siyi_sdk import SIYISDK

window = tk.Tk()
window.title('SiYi Ground Control ( ͡❛ ͜ʖ ͡❛)')
window.geometry('320x240')

class CamAngle:
    def __init__(self):
        self.yaw = 0
        self.pitch = 0

    def addYaw(self, dy):
        self.yaw += dy
        # Clamp yaw - adjust these limits per your camera specs
        self.yaw = max(-45, min(45, self.yaw))

    def addPitch(self, dp):
        self.pitch += dp
        # Clamp pitch - adjust these limits per your camera specs
        self.pitch = max(-90, min(25, self.pitch))

    def zeroYaw(self):
        self.yaw = 0

    def zeroPitch(self):
        self.pitch = 0

cam_angle = CamAngle()
cam = SIYISDK(server_ip="192.168.144.25", port=37260)

if not cam.connect():
    print("No connection")
    exit(1)

cam.requestFollowMode()

def update_gimbal():
    cam.setGimbalRotation(cam_angle.yaw, cam_angle.pitch)
    attitude = cam.getAttitude()
    print(f"Set angles - Yaw: {cam_angle.yaw}, Pitch: {cam_angle.pitch} | Attitude: {attitude}")

def pitch_up():
    cam_angle.addPitch(5)
    update_gimbal()

def pitch_down():
    cam_angle.addPitch(-5)
    update_gimbal()

def yaw_left():
    cam_angle.addYaw(5)
    update_gimbal()

def yaw_right():
    cam_angle.addYaw(-5)
    update_gimbal()

def pitch_yaw_center():
    cam_angle.zeroYaw()
    cam_angle.zeroPitch()
    update_gimbal()

pitch_up_button = ttk.Button(window, text='🢁', command=pitch_up)
pitch_up_button.grid(row=0, column=1, pady=2)

pitch_down_button = ttk.Button(window, text='🢃', command=pitch_down)
pitch_down_button.grid(row=2, column=1, pady=2)

yaw_left_button = ttk.Button(window, text='🢀', command=yaw_left)
yaw_left_button.grid(row=1, column=0, pady=2)

yaw_right_button = ttk.Button(window, text='🢂', command=yaw_right)
yaw_right_button.grid(row=1, column=2, pady=2)

center_button = ttk.Button(window, text='🎯', command=pitch_yaw_center)
center_button.grid(row=1, column=1, pady=2)

def zoom_in():
    cam.requestZoomIn()
    sleep(0.5)
    cam.requestZoomHold()
    sleep(0.5)
    print("Zoom level:", cam.getZoomLevel())

zoom_in_button = ttk.Button(window, text='🔎➕', command=zoom_in)
zoom_in_button.grid(row=3, column=0, pady=2)

def zoom_out():
    cam.requestZoomOut()
    sleep(0.5)
    cam.requestZoomHold()
    sleep(0.5)
    print("Zoom level:", cam.getZoomLevel())

zoom_out_button = ttk.Button(window, text='🔎➖', command=zoom_out)
zoom_out_button.grid(row=3, column=2, pady=2)

window.mainloop()
cam.disconnect()
print("exit")
