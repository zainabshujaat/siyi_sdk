import tkinter as tk
from tkinter import ttk
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
        if self.yaw > 45:
            self.yaw = 45
        if self.yaw < -45:
            self.yaw = -45

    def addPitch(self, dp):
        self.pitch += dp
        if self.pitch > 25:
            self.pitch = 25
        if self.pitch < -90:
            self.pitch = -90

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
    print("Pitch Up pressed")
    cam_angle.addPitch(5)
    update_gimbal()

def pitch_down():
    print("Pitch Down pressed")
    cam_angle.addPitch(-5)
    update_gimbal()

def yaw_left():
    print("Yaw Left pressed")
    cam_angle.addYaw(5)
    update_gimbal()

def yaw_right():
    print("Yaw Right pressed")
    cam_angle.addYaw(-5)
    update_gimbal()

def pitch_yaw_center():
    print("Centering gimbal")
    cam_angle.zeroYaw()
    cam_angle.zeroPitch()
    update_gimbal()

def zoom_in_step2():
    cam.requestZoomHold()
    print("Zoom level:", cam.getZoomLevel())

def zoom_in():
    print("Zoom In pressed")
    cam.requestZoomIn()
    window.after(500, zoom_in_step2)

def zoom_out_step2():
    cam.requestZoomHold()
    print("Zoom level:", cam.getZoomLevel())

def zoom_out():
    print("Zoom Out pressed")
    cam.requestZoomOut()
    window.after(500, zoom_out_step2)

# Layout buttons

pitch_up_button = ttk.Button(window, text='🢁', command=pitch_up)
pitch_up_button.grid(row=0, column=1, pady=2)

pitch_down_button = ttk.Button(window, text='🢃', command=pitch_down)
pitch_down_button.grid(row=2, column=1, pady=2)

yaw_left_button = ttk.Button(window, text='🢀', command=yaw_left)
yaw_left_button.grid(row=1, column=0, pady=2)

yaw_right_button = ttk.Button(window, text='🢂', command=yaw_right)
yaw_right_button.grid(row=1, column=2, pady=2)

pitch_yaw_center_button = ttk.Button(window, text='🎯', command=pitch_yaw_center)
pitch_yaw_center_button.grid(row=1, column=1, pady=2)

zoom_in_button = ttk.Button(window, text='🔎➕', command=zoom_in)
zoom_in_button.grid(row=3, column=0, pady=2)

zoom_out_button = ttk.Button(window, text='🔎➖', command=zoom_out)
zoom_out_button.grid(row=3, column=2, pady=2)

window.mainloop()
cam.disconnect()
print("exit")
