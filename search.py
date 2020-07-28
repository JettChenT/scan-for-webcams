import os
import shodan
import requests
import socket
import urllib
from PIL import Image, ImageEnhance
from rich import print


class Scanner(object):
    def __init__(self):
        socket.setdefaulttimeout(5)
        self.SHODAN_API_KEY = os.environ.get("SHODAN_API_KEY")
        self.api = shodan.Shodan(self.SHODAN_API_KEY)
        # preset url schemes
        self.default_url_scheme = "[link=http://{ip}:{port}][i][green]{ip}[/green]:[red]{port}[/red][/link]"
        self.MJPG_url_scheme = "[link=http://{ip}:{port}/?action=stream][i]http://[green]{ip}[/green]:[red]{port}[/red]" \
                               "[blue]/?action=stream[/blue][/link]"

    def check_empty(self,image_source,tolerance=5)->bool:
        im_loc = "tmp.png"
        urllib.request.urlretrieve(image_source, im_loc)
        im = Image.open(im_loc)
        extrema = im.convert("L").getextrema()
        if abs(extrema[0]-extrema[1]) <= tolerance:
            return False
        return True

    def scan(self, camera_type, url_scheme = '', check_empty=''):
        if url_scheme == '':
            url_scheme = self.default_url_scheme

        results = self.api.search("webcams")
        max_time = len(results["matches"])*10
        print(f"maximum time:{max_time} seconds")
        for result in results["matches"]:
            if camera_type in result["data"]:
                url = f"http://{result['ip_str']}:{result['port']}"
                try:
                    r = requests.get(url, timeout=5)
                    if r.status_code == 200:
                        if check_empty == "":
                            print(
                                url_scheme.format(ip=result['ip_str'], port=result['port'])
                            )
                            continue
                        if self.check_empty(check_empty.format(url=url)):
                            print(
                                url_scheme.format(ip=result['ip_str'], port=result['port'])
                            )
                except:
                    continue

    def MJPG(self):
        scheme = self.MJPG_url_scheme
        self.scan("MJPG-streamer", url_scheme=scheme, check_empty="{url}/?action=snapshot")

    def webcamXP(self):
        self.scan("webcamXP")