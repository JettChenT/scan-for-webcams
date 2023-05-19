import os
import traceback
import sys
import shodan
import warnings
import socket
import json
from PIL import Image
from rich import print
from halo import Halo
from dotenv import load_dotenv
from pathlib import Path
from geoip import Locater
from crfi import Clarifai
from cam import get_cam, CameraEntry, Camera

def handle():
    err = sys.exc_info()[0]
    print("[red]ERROR:[/red]")
    print(err)
    print(traceback.format_exc())

class Scanner(object):
    def __init__(self):
        socket.setdefaulttimeout(5)
        directory = Path(__file__).parent
        env_path = directory / ".env"
        load_dotenv(override=True, dotenv_path=env_path)
        self.SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
        if self.SHODAN_API_KEY is None:
            raise KeyError("Shodan API key not found in envrion")
        self.api = shodan.Shodan(self.SHODAN_API_KEY)
        # preset url schemes
        self.clarifai = self.locator = self.places = None
        self.cli = True
        with open(directory / "cams.json") as f:
            self.config = json.load(f)

    def init_clarifai(self):
        self.CLARIFAI_API_KEY = os.getenv("CLARIFAI_API_KEY")
        if self.CLARIFAI_API_KEY is None:
            raise KeyError("Clarifai API key not found in environ")
        self.clarifai = Clarifai(self.CLARIFAI_API_KEY)

    def init_geoip(self):
        self.GEOIP_API_KEY = os.getenv("GEOIP_API_KEY")
        if self.GEOIP_API_KEY is None:
            raise KeyError("Geoip API key not found in environ")
        self.locator = Locater(self.GEOIP_API_KEY)

    def init_places(self):
        try:
            from places_mod import Places
            self.places = Places()
        except ImportError as e:
            warnings.warn("Please make sure you have torch and torchvision installed to use this feature")
            raise e
        except Exception as e:
            print(f"Unexpected Error: {e}")

    def tag_image(self, url):
        concepts = self.clarifai.get_concepts(url)
        return concepts

    def check_empty(self, im: Image, tolerance=5) -> bool:
        extrema = im.convert("L").getextrema()
        if abs(extrema[0] - extrema[1]) <= tolerance:
            return False
        return True

    def output(self, *args, **kwargs):
        if(self.cli):
            print(*args, **kwargs)

    def scan(
            self,
            cam: Camera,
            check_empty=True,
            tag=True,
            geoip=True,
            places=False,
            debug=False,
            add_query=""
    ):
        print(f"loc:{geoip}, check_empty:{check_empty}, clarifai:{tag}, places:{places}")
        query = cam.query + " " + add_query
        if debug:
            print(f"Searching for: {query}")
        else:
            os.environ["OPENCV_LOG_LEVEL"] = "OFF"
        if self.SHODAN_API_KEY == "":
            print("[red]Please set up shodan API key in environ![/red]")
            return
        spinner = Halo(text="Initializing...", spinner="dots")
        spinner.start()
        if tag and (self.clarifai is None):
            self.init_clarifai()
        if geoip and (self.locator is None):
            self.init_geoip()
        if places and (self.places is None):
            self.init_places()
        spinner.succeed()
        spinner = Halo(text="Looking for possible servers...", spinner="dots")
        spinner.start()
        try:
            results = self.api.search(query)
            spinner.succeed("Done")
        except Exception as e:
            spinner.fail(f"Get data from API failed: {e}")
            if debug:
                handle()
            return
        max_time = len(results["matches"]) * 10
        print(f"maximum time: {max_time} seconds")
        camera_type_list = []
        for result in results["matches"]:
            if cam.camera_type is None or cam.camera_type in result["data"]:
                camera_type_list.append(result)
        store = []
        cnt = 0
        for result in camera_type_list:
            entry = CameraEntry(result['ip_str'], int(result['port']))
            cnt += 1
            try:
                if cam.check_accessible(entry):
                    store.append({})
                    if not check_empty:
                        if(debug): print("not check empty")
                        self.output(
                            cam.get_display_url(entry)
                        )
                    else:
                        if(debug): print(f"checking...")    
                        is_empty = self.check_empty(cam.get_image(entry))
                        if(debug): print(f"check empty: {is_empty}")    
                        if is_empty:
                            store[-1] = result
                            self.output(
                                cam.get_display_url(entry)
                            )
                        else:
                            spinner.close()
                            continue
                    if geoip:
                        country, region, hour, minute = self.locator.locate(result["ip_str"])
                        self.output(f":earth_asia:[green]{country} , {region} {hour:02d}:{minute:02d}[/green]")
                        store[-1]["country"] = country
                        store[-1]["region"] = region
                    if tag:
                        tags = self.tag_image(cam.get_image(entry))
                        for t in tags:
                            self.output(f"|[green]{t}[/green]|", end=" ")
                        if len(tags) == 0:
                            self.output("[i green]no description[i green]", end="")
                        print()
                        store[-1]["tags"] = tags
                    if places:
                        im = cam.get_image(entry)
                        self.output(self.places.output(im))
                    # spinner.close()
                    print()
            except KeyboardInterrupt:
                print("[red]terminating...")
                break
            except:
                if debug:
                    handle()
                else:
                    continue

    def testfunc(self, **kwargs):
        print(kwargs)

    def scan_preset(self, preset, check, tag,places, loc,debug=False, add_query=""):
        if preset not in self.config:
            raise KeyError("The preset entered doesn't exist")
        for key in self.config[preset]:
            if self.config[preset][key] == "[def]":
                self.config[preset][key] = self.config["default"][key]
        print('beginning scan...')
        cam = get_cam(**self.config[preset])
        self.scan(cam, check, tag, loc, places, debug, add_query)
        print('scan finished')
