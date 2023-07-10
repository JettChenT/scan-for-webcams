import PySimpleGUI as sg
from PIL import Image
import io
import numpy as np
from PIL import Image

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
    if im is None:
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
            
            self.update_images()
            # Check if the number of streams has changed
            if not self.fixed and len(self.stream_manager) != self.prev_stream_count:
                self.prev_stream_count = len(self.stream_manager)
                self.create_window()


        self.window.close()
