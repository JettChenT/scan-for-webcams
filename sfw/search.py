import os
import traceback
import sys
import shodan
import requests
import warnings
import socket
import urllib
import json
from PIL import Image
from rich import print
from halo import Halo
from dotenv import load_dotenv
from pathlib import Path
from geoip import Locater
from crfi import Clarifai

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

    def check_empty(self, image_source, tolerance=5) -> bool:
        im_loc = ".tmpimage"
        urllib.request.urlretrieve(image_source, im_loc)
        im = Image.open(im_loc)
        extrema = im.convert("L").getextrema()
        if abs(extrema[0] - extrema[1]) <= tolerance:
            return False
        return True

    def output(self, *args, **kwargs):
        if(self.cli):
            print(*args, **kwargs)

    def scan(
            self,
            camera_type,
            url_scheme="",
            check_empty_url="",
            check_empty=True,
            tag=True,
            geoip=True,
            places=False,
            search_q="webcams",
            debug=False
    ):
        print(f"loc:{geoip}, check_empty:{check_empty}, tag:{tag}")
        if url_scheme == "":
            url_scheme = self.config["default"]["url_scheme"]
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
            results = self.api.search(search_q)
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
            if camera_type in result["data"]:
                camera_type_list.append(result)
        store = []
        cnt = 0
        for result in camera_type_list:
            url = f"http://{result['ip_str']}:{result['port']}"
            cnt += 1
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    if not check_empty:
                        self.output(
                            url_scheme.format(ip=result["ip_str"], port=result["port"])
                        )
                    else:
                        is_empty = self.check_empty(check_empty_url.format(url=url))
                        if is_empty:
                            store.append(result)
                            self.output(
                                url_scheme.format(
                                    ip=result["ip_str"], port=result["port"]
                                )
                            )
                        else:
                            spinner.close()
                            continue
                    if geoip:
                        country, region, hour, minute = self.locator.locate(result["ip_str"])
                        self.output(f":earth_asia:[green]{country} , {region} {hour}:{minute}[/green]")
                        store[-1]["country"] = country
                        store[-1]["region"] = region
                    if tag:
                        tags = self.tag_image(check_empty_url.format(url=url))
                        for t in tags:
                            self.output(f"|[green]{t}[/green]|", end=" ")
                        if len(tags) == 0:
                            self.output("[i green]no description[i green]", end="")
                        print()
                        store[-1]["tags"] = tags
                    if places:
                        if self.check_empty(check_empty_url.format(url=url)):
                            self.output(self.places.output(".tmpimage"))
                        else:
                            self.output("[i red]footage is empty, skipping places[/i red]")

                    # spinner.close()
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

    def scan_preset(self, preset, check, tag,places, loc,debug=False):
        if preset not in self.config:
            raise KeyError("The preset entered doesn't exist")
        for key in self.config[preset]:
            if self.config[preset][key] == "[def]":
                self.config[preset][key] = self.config["default"][key]
        config = self.config[preset]
        config["check_empty"] = check
        config["tag"] = tag
        config["geoip"] = loc
        config['debug'] = debug
        config['places'] = places
        print('beginning scan...')
        self.scan(**config)
        print('scan finished')
