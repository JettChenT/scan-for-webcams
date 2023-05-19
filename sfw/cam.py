from dataclasses import dataclass
from PIL import Image
import requests
from rtsp import attack, capture
import contextlib
import os

DEF_URL_SCHEME = "[link=http://{ip}:{port}]http://[i][green]{ip}[/green]:[red]{port}[/red][/link]"

class CameraEntry:
    def __init__(self, ip: str, port: int, store: dict = {}):
        self.ip = ip
        self.port = port
        self.store = store

    def fmt(self, url_scheme) -> str:
        return url_scheme.format(ip=self.ip, port=self.port)

class Camera:
    def __init__(self, query:str, camera_type:str|None=None) -> None:
        self.query = query
        self.camera_type = camera_type

    def get_display_url(self, entry: CameraEntry) -> str | None:
        """Returns the displayed stream url"""
        pass

    def get_image(self, entry: CameraEntry) -> Image:
        pass

    def check_accessible(self, entry: CameraEntry) -> bool:
        """Returns True if the camera is accessible"""
        pass
    

class WebCamera(Camera):
    def __init__(self,
                capture_url:str,
                query:str = "webcams",
                display_url_scheme: str = DEF_URL_SCHEME,
                camera_type: str|None = None
                ) -> None:
        super().__init__(query, camera_type)
        self.capture_url = capture_url
        self.display_url_scheme = display_url_scheme
    
    def get_display_url(self, entry: CameraEntry) -> str:
        return self.display_url_scheme.format(ip=entry.ip, port=entry.port)
    
    def get_base_url(self, entry: CameraEntry) -> str:
        return f"http://{entry.ip}:{entry.port}"

    def get_image_url(self, entry: CameraEntry) -> str:
        return self.capture_url.format(url=self.get_base_url(entry))
    
    def get_image(self, entry: CameraEntry) -> Image:
        """download image from url from get_image_url"""
        url = self.get_image_url(entry)
        return Image.open(requests.get(url, stream=True, timeout=5).raw)
    
    def check_accessible(self, entry: CameraEntry) -> bool:
        return requests.get(self.get_base_url(entry), timeout=5).status_code == 200

class RTSPCamera(Camera):
    def __init__(self, query: str, camera_type: str | None = None,
                 stream_url_scheme:str|None = None
                 ) -> None:
        super().__init__(query, camera_type)
        self.stream_url_scheme = stream_url_scheme
    
    def get_display_url(self, entry: CameraEntry) -> str | None:
        if self.stream_url_scheme is None:
            stream_url = attack(entry.ip, entry.port)
        else:
            url = entry.fmt("rtsp://{ip}:{port}")
            stream_url = self.stream_url_scheme.format(url=url)
        entry.store["stream_url"] = stream_url
        return stream_url
    
    def get_image(self, entry: CameraEntry) -> Image:
        if entry.store.get("stream_url") is None:
            self.get_display_url(entry)
        res = capture(entry.store["stream_url"])
        if res is None:
            raise Exception("Failed to capture image")
        return Image.fromarray(res)
    
    def check_accessible(self, entry: CameraEntry) -> bool:
        return self.get_display_url(entry) is not None

def get_cam(
        protocol: str|None = None, **kwargs) -> Camera:
    if protocol=="rtsp":
        return RTSPCamera(**kwargs)
    return WebCamera(**kwargs)