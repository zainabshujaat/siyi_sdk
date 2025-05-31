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

class GimbalControl:
    def __init__(self, sdk):
        self.sdk = sdk
        self.lock = threading.Lock()

    def _get_safe_attitude(self):
        attitude = self.sdk.getAttitude()
        if attitude is None or len(attitude) < 2:
            return 0, 0
        return attitude[0], attitude[1]  # yaw, pitch

    def move(self, dyaw=0, dpitch=0):
        def _threaded_move():
            with self.lock:
                yaw, pitch = self._get_safe_attitude()
                yaw += dyaw
                pitch += dpitch
                yaw = max(min(yaw, 45), -45)
                pitch = max(min(pitch, 25), -90)
                print(f"[MOVE] Yaw: {yaw}, Pitch: {pitch}")
                self.sdk.setGimbalRotation(yaw, pitch)
        threading.Thread(target=_threaded_move).start()

    def center(self):
        def _center():
            with self.lock:
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

gimbal = GimbalControl(cam)

# Button callbacks
def pitch_up(): gimbal.move(dpitch=2)
def pitch_down(): gimbal.move(dpitch=-2)
def yaw_left(): gimbal.move(dyaw=2)
def yaw_right(): gimbal.move(dyaw=-2)
def pitch_yaw_center(): gimbal.center()
def zoom_in(): gimbal.zoom_in()
def zoom_out(): gimbal.zoom_out()

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

