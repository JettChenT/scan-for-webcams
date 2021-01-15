from .search import Scanner
import fire
from rich import print
from pathlib import Path

class CLI:
    def __init__(self):
        try:
            self.scanner = Scanner()
        except KeyError:
            print("[red] API key not found")
            print("Please set up first:")
            self.setup()

    def setup(self):
        SHODAN_API_KEY = input("Please enter your SHODAN API KEY:")
        CLARIFAI_API_KEY = input("Please enter your CLARIFAI API KEY:")
        with open (Path(__file__).parent/'.env', 'w') as f:
            f.write(f"SHODAN_API_KEY={SHODAN_API_KEY}\n")
            f.write(f"CLARIFAI_API_KEY={CLARIFAI_API_KEY}")
            
    def status(self):
        print("Status [green]OK[/green]!")

    def search(self,preset,check=True,tag=True,store=False,loc=False):
        """
        :param preset: string, the type of pre written camera you want. choose from: 1)"webcamXP" 2)"MJPG 3)"yawCam"
        :param check: boolean, indicates whether or not you want to check if the image is completly black or white.
        :param tag: boolean, indicates whether or not you want to generate descriptions for the webcam.
        """
        self.scanner.scan_preset(preset,check,tag,loc)

    def search_custom(self,camera_type, url_scheme = '', check_empty_url='',check_empty = True, tag=True, search_q="webcams"):
        """
        :param camera_type: string, the type of camera. this string must appear in the data returned by shodan
        :param url_scheme: string, the format in which the result will be displayed
        :param check_empty_url: string, the format that leads to an image that could be downloaded
        :param check_empty: boolean, indicates whether or not you want to check if the image is completly black or white
        :param tag: boolean, indicates whether or not you want to generate descriptions for the image
        :param search_q: string, the term to search for in shodan
        """
        self.scanner.scan(camera_type=camera_type,url_scheme=url_scheme,check_empty_url=check_empty_url,
                       check_empty=check_empty,tag=tag,search_q=search_q)