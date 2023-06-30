from cam import RTSPCamera, CameraEntry
import time
import threading
import cv2 as cv
import av

hipcam = RTSPCamera("hipcam", stream_url_scheme="{url}/11")

hipcam_links = [
    "125.71.206.54",
    "112.249.65.151",
    "122.195.121.138",
    "58.252.182.248",
    "110.251.115.21",
    "119.39.123.162",
    "120.237.216.51",
    "114.83.4.114"
]

imgstore = {}

def retrieve(ip):
    ce = CameraEntry(ip, 554)
    print(f"retrieve {ip}")
    im = hipcam.get_image(ce)
    print(ip, im.size)
    imgstore[ip] = im

def retrieve_all_parallel():
    st = time.time()
    threads = []
    for ip in hipcam_links:
        t = threading.Thread(target=retrieve, args=(ip,), daemon=True)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print(f"parallel done, time taken: {time.time() - st} seconds")


def retrieve_all_serial():
    st = time.time()
    for ip in hipcam_links:
        retrieve(ip)
    print(f"serial done, time taken: {time.time() - st} seconds")
    imgstore[hipcam_links[0]].show()

def test_parallel_vs_serial():
    retrieve_all_parallel()
    global imgstore
    imgstore = {}
    retrieve_all_serial()

test_parallel_vs_serial()