from .search import Scanner
import fire
from rich import print
from pathlib import Path
from dotenv import load_dotenv
import os


class CLI:
    def init_scanner(self):
        try:
            self.scanner = Scanner()
        except KeyError:
            print("[red] API key not found")
            print("Please set up first:")
            self.setup()

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

    def search(self, preset, check=True, tag=True, store=False, loc=True):
        """
        :param preset: string, the type of pre written camera you want. choose from: 1)"webcamXP" 2)"MJPG 3)"yawCam"
        :param check: boolean, indicates whether or not you want to check if the image is completly black or white.
        :param tag: boolean, indicates whether or not you want to generate descriptions for the webcam.
        """
        self.init_scanner()
        self.scanner.scan_preset(preset, check, tag, loc)

    def search_custom(
        self,
        camera_type,
        url_scheme="",
        check_empty_url="",
        check_empty=True,
        tag=True,
        loc=True,
        search_q="webcams",
    ):
        """
        :param camera_type: string, the type of camera. this string must appear in the data returned by shodan
        :param url_scheme: string, the format in which the result will be displayed
        :param check_empty_url: string, the format that leads to an image that could be downloaded
        :param check_empty: boolean, indicates whether or not you want to check if the image is completly black or white
        :param tag: boolean, indicates whether or not you want to generate descriptions for the image
        :param search_q: string, the term to search for in shodan
        """
        self.init_scanner()
        self.scanner.scan(
            camera_type=camera_type,
            url_scheme=url_scheme,
            check_empty_url=check_empty_url,
            check_empty=check_empty,
            tag=tag,
            search_q=search_q,
            loc=loc
        )

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
