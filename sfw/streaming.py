import PySimpleGUI as sg
from PIL import Image
import io
from cam import RTSPCamera, CameraEntry
import threading
import cv2 as cv
import numpy as np
from dataclasses import dataclass
from cam import Camera
from typing import Any, List
from PIL import Image

@dataclass
class StreamRecord:
    camera: Camera
    camera_entry: CameraEntry


class StreamManager:
    def __init__(self, streamrecords: List[StreamRecord]=list()) -> None:
        self.streamrecords = streamrecords
        self.streamData: dict[CameraEntry, None|Image.Image] = {sr.camera_entry: None for sr in streamrecords}
        self.threads = []
        for sr in streamrecords:
            self.start_stream(sr)
    
    def start_stream(self, sr: StreamRecord):
        def thread():
            for frame in sr.camera.stream(sr.camera_entry):
                self.streamData[sr.camera_entry] = frame
        threading.Thread(target=thread, daemon=True).start()
        self.threads.append(thread)
    
    def __getitem__(self, key: CameraEntry|int) -> None|Image.Image:
        if type(key) == int:
            if key >= len(self.streamrecords):
                return None
            return self.streamData[self.streamrecords[key].camera_entry]
        elif type(key) == CameraEntry: # eh stoopid pylance
            return self.streamData[key]
        
    def __iter__(self):
        return iter(self.streamrecords)
        
    def __len__(self):
        return len(self.streamrecords)

    def add(self, sr: StreamRecord):
        self.streamrecords.append(sr)
        self.streamData[sr.camera_entry] = None
        self.start_stream(sr)
    
    def insert(self, index: int, sr: StreamRecord):
        self.streamrecords.insert(index, sr)
        self.streamData[sr.camera_entry] = None
        self.start_stream(sr)