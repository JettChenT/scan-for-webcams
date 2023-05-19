from search import Scanner
from rich import print
from pathlib import Path
from dotenv import load_dotenv
import os
import rtsp
import json

class CLI:
    def init_scanner(self):
        try:
            self.scanner = Scanner()
        except KeyError:
            print("[red] API key not found")
            print("Please set up first:")
            self.setup()
            self.init_scanner()

    def setup(self):
        SHODAN_API_KEY = input("Please enter your SHODAN API KEY:")
        CLARIFAI_API_KEY = input("Please enter your CLARIFAI API KEY:")
        GEOIP_API_KEY = input("Please enter your GEOIP API KEY:")
        with open(Path(__file__).parent / ".env", "w") as f:
            f.write(f"SHODAN_API_KEY={SHODAN_API_KEY}\n")
            f.write(f"CLARIFAI_API_KEY={CLARIFAI_API_KEY}\n")
            f.write(f"GEOIP_API_KEY={GEOIP_API_KEY}")

    def status(self):
        print("Status [green]OK[/green]!")

    def search(self, preset, check=True, tag=True, store=None, loc=True, places=False, debug=False, protocol=None, query=""):
        """
        :param preset: string, the type of pre written camera you want. choose from: 1)"webcamXP" 2)"MJPG 3)"yawCam" 4) "rtsp"
        :param check: boolean, indicates whether or not you want to check if the image is completly black or white.
        :param tag: boolean, indicates whether or not you want to generate descriptions for the webcam.
        :param store: (optional)string, indicates the location where you want to save the results.
        :param places: boolean, indicates whether or not you want to generate descriptions for the webcam with the "places" model.
        :param debug: boolean, indicates whether or not you want to print debug info.
        :param protocol: string, the protocol to use. choose from: 1)"http" 2)"rtsp"
        :param query: string, additional query to add to the search, can be shodan filters or anything else.
        """
        self.init_scanner()
        res = self.scanner.scan_preset(preset, check, tag, loc,places, debug, query)
        if store:
            json.dump(res, open(store, 'r'))

    def search_custom(
        self,
        camera_type,
        url_scheme="",
        check_empty_url="",
        check_empty=True,
        tag=True,
        loc=True,
        places=False,
        store = False,
        search_q="webcams",
        debug=False
    ):
        """
        :param camera_type: string, the type of camera. this string must appear in the data returned by shodan
        :param url_scheme: string, the format in which the result will be displayed
        :param check_empty_url: string, the format that leads to an image that could be downloaded
        :param check_empty: boolean, indicates whether or not you want to check if the image is completly black or white
        :param tag: boolean, indicates whether or not you want to generate descriptions for the image
        :param store: (optional)string, indicates the location where you want to save the results.
        :param search_q: string, the term to search for in shodan
        :param debug: boolean, indicates whether or not you want to print debug info.
        """
        self.init_scanner()
        res = self.scanner.scan(
            camera_type=camera_type,
            url_scheme=url_scheme,
            check_empty_url=check_empty_url,
            check_empty=check_empty,
            tag=tag,
            search_q=search_q,
            loc=loc,
            places=places,
            debug=debug
        )
        if store:
            json.dump(res, open(store, 'r'))

    def show_environ(self):
        directory = Path(__file__).parent
        env_path = directory / ".env"
        load_dotenv(override=True, dotenv_path=env_path)
        shodan = os.getenv("SHODAN_API_KEY")
        clarifai = os.getenv("CLARIFAI_API_KEY")
        geoip = os.getenv("GEOIP_API_KEY")
        print(f"shodan api key:{shodan}")
        print(f"clarifai api key: {clarifai}")
        print(f"geoip api key: {geoip}")
    
    def play(self, url:str):
        """
        :param url: string, the url of the webcam
        """
        if url.startswith("rtsp"):
            rtsp.play(url)
        else:
            os.system(f"open {url}")