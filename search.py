import os
import shodan
import requests
import socket
import urllib
from PIL import Image, ImageEnhance
from rich import print
from clarifai.rest import ClarifaiApp
from halo import Halo
from dotenv import load_dotenv

class Scanner(object):
    def __init__(self):
        socket.setdefaulttimeout(5)
        load_dotenv(override=True)
        self.SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
        if self.SHODAN_API_KEY == None:
            raise KeyError("Shodan API key not found in envrion")
        self.api = shodan.Shodan(self.SHODAN_API_KEY)
        # preset url schemes
        self.default_url_scheme = "[link=http://{ip}:{port}]http://[i][green]{ip}[/green]:[red]{port}[/red][/link]"
        self.MJPG_url_scheme = "[link=http://{ip}:{port}/?action=stream][i]http://[green]{ip}[/green]:[red]{port}[/red]" \
                               "[blue]/?action=stream[/blue][/link]"
        self.clarifai_initialized = False

    def init_clarifai(self):
        self.CLARIFAI_API_KEY = os.getenv("CLARIFAI_API_KEY")
        if self.CLARIFAI_API_KEY == None:
            raise KeyError("Clarifai API key not found in environ")
        self.clarifai_app = ClarifaiApp(api_key=self.CLARIFAI_API_KEY)
        self.clarifai_model = self.clarifai_app.public_models.general_model
        self.clarifai_initialized = True

    def tag_image(self,url):
        response = self.clarifai_model.predict_by_url(url=url)
        results = [concept['name'] for concept in response['outputs'][0]['data']['concepts']]
        return results

    def check_empty(self,image_source,tolerance=5)->bool:
        im_loc = ".tmpimage"
        urllib.request.urlretrieve(image_source, im_loc)
        im = Image.open(im_loc)
        extrema = im.convert("L").getextrema()
        if abs(extrema[0]-extrema[1]) <= tolerance:
            return False
        return True

    def scan(self, camera_type, url_scheme = '', check_empty_url='',check_empty = True, tag=True, search_q="webcams"):
        if url_scheme == '':
            url_scheme = self.default_url_scheme
        if self.SHODAN_API_KEY == '':
            print("[red]Please set up shodan API key in environ![/red]")
            return
        spinner = Halo(text='Looking for possible servers...', spinner='dots')
        spinner.start()
        if tag and (not self.clarifai_initialized):
            self.init_clarifai()
        try:
            results = self.api.search(search_q)
            spinner.succeed("Done")
        except:
            spinner.fail("Get data from API failed")
            return
        max_time = len(results["matches"])*10
        print(f"maximum time:{max_time} seconds")
        camera_type_list = []
        for result in results["matches"]:
            if camera_type in result["data"]:
                camera_type_list.append(result)
        cnt = 0
        for result in camera_type_list:
            url = f"http://{result['ip_str']}:{result['port']}"
            cnt+=1
            print(f"{cnt}/{len(camera_type_list)}")
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    if check_empty == False:
                        print(
                            url_scheme.format(ip=result['ip_str'], port=result['port'])
                        )
                    else:
                        is_empty = self.check_empty(check_empty_url.format(url=url))
                        if is_empty:
                            print(
                                url_scheme.format(ip=result['ip_str'], port=result['port'])
                            )
                        else:
                            spinner.close()
                            continue
                    if tag:
                        tags = self.tag_image(check_empty_url.format(url=url))
                        for t in tags:
                            print(f"|[green]{t}[/green]|",end=" ")
                        if len(tags)==0:
                            print("[i green]no description[i green]",end="")
                        print()
                    spinner.close()
                else:
                    print("[red]webcam not avaliable[/red]")
            except KeyboardInterrupt:
                print("[red]terminating...")
                break
            except:
                continue

    def MJPG(self,check,tag):
        scheme = self.MJPG_url_scheme
        self.scan("MJPG-streamer", url_scheme=scheme, check_empty=check,check_empty_url="{url}/?action=snapshot",tag=tag)

    def webcamXP(self,check,tag):
        self.scan("webcamXP", check_empty=check, check_empty_url='{url}/cam_1.jpg', tag=tag, search_q='product:webcamXP')

    def yawCam(self,check,tag):
        self.scan("", check_empty=check,check_empty_url="{url}/out.jpg",tag=tag,search_q='product:yawCam')