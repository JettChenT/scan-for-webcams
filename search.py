import os
import shodan
import requests
from rich import print

class Scanner(object):
    def __init__(self):
        self.SHODAN_API_KEY = os.environ.get("SHODAN_API_KEY")
        self.api = shodan.Shodan(self.SHODAN_API_KEY)

    def scan(self, camera_type):
        results = self.api.search("webcams")
        for result in results["matches"]:
            if camera_type in result["data"]:
                url = f"http://{result['ip_str']}:{result['port']}"
                try:
                    r = requests.get(url, timeout=5)
                    if r.status_code == 200:
                        print(
                            f"[link={url}][i][green]{result['ip_str']}[/green]:[red]{result['port']}[/red][/link]"
                        )
                except:
                    continue

    def MJPG(self):
        self.scan("MJPG-streamer")

    def webcamXP(self):
        self.scan("webcamXP")