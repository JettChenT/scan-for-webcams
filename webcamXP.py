import shodan
import requests
from rich import print

SHODAN_API_KEY = "j0B1M6qtOeGtKixNyAPtJV0Oj44Pg90Y"
api = shodan.Shodan(SHODAN_API_KEY)
try:
    results = api.search('webcam')
except:
    print("error!")

for result in results['matches']:
    if "webcamXP" in result['data']:
        url = f"http://{result['ip_str']}:{result['port']}"
        try:
            r = requests.get(url,timeout=5)
            if r.status_code == 200:
                print(f"[link={url}][i][green]{result['ip_str']}[/green]:[red]{result['port']}[/red][/link]")
        except:
            continue