import PySimpleGUI as sg
from PIL import Image
import io
from cam import WebCamera, RTSPCamera, CameraEntry
import cv2 as cv
import numpy as np
from dataclasses import dataclass
from cam import Camera
from typing import Any, List
from PIL import Image
from streaming import StreamManager, StreamRecord
from threading import Thread
import time
from search import Scanner

webcamXP = WebCamera("{url}/cam_1.jpg")
urls = [
    "180.145.170.192:8008"
]

entries = []
for url in urls:
    ip, port = url.split(":")
    entries.append(CameraEntry(ip, int(port)))
records = [StreamRecord(webcamXP, entry) for entry in entries]
stream_manager = StreamManager(records)

DIMENSIONS = (200, 400)

def get_img_data(f, maxsize=(1200, 850)):
    """Generate image data using PIL
    """
    img = Image.fromarray(f)
    img.thumbnail(maxsize)

    if img.mode != 'RGB':
        img = img.convert('RGB')

    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()


def imgtobytes(im):
    if im==None:
        im = np.zeros(DIMENSIONS)
    if type(im) == np.ndarray:
        return get_img_data(im)
    with io.BytesIO() as bio:
        im.thumbnail((1200,200))
        im.save(bio, format="PNG")
        return bio.getvalue()


class WebcamGUI:
    WIDTH = 4
    DISPLAY_COUNT = 16
    def __init__(self, stream_manager, fixed=True):
        self.stream_manager = stream_manager
        self.window = None
        self.prev_stream_count = len(self.stream_manager)
        self.fixed = fixed

    def generate_layout(self):
        layout = []
        row = []
        for i in range(self.DISPLAY_COUNT if self.fixed else len(self.stream_manager)):
            if i % self.WIDTH == 0 and i > 0:
                layout.append(row)
                row = []
            row.append(sg.Image(data=imgtobytes(self.stream_manager[i]), key=i))
        if row:
            layout.append(row)
        return layout

    def create_window(self):
        layout = self.generate_layout()
        if self.window:
            self.window.close()
        self.window = sg.Window('Webcams', layout, finalize=True)

    def update_images(self):
        for i in range(len(self.stream_manager)):
            self.window[i].update(data=imgtobytes(self.stream_manager[i]))

    def run(self):
        self.create_window()

        while True:
            event, values = self.window.read(timeout=25)
            if event == sg.WINDOW_CLOSED:
                break
            
            # Check if the number of streams has changed
            if not self.fixed and len(self.stream_manager) != self.prev_stream_count:
                self.prev_stream_count = len(self.stream_manager)
                self.create_window()

            self.update_images()

        self.window.close()


def tst_insert_urls(stream_manager: StreamManager):
    scanner = Scanner()
    scanner.scan_preset('MJPG', False, False, False, False, stream_manager=stream_manager)

if __name__ == "__main__":
    thread = Thread(target=tst_insert_urls, args=(stream_manager,))
    thread.start()
    gui = WebcamGUI(stream_manager)
    gui.run()
