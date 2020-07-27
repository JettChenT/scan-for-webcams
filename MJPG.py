import os
import shodan
import requests
from rich import print

SHODAN_API_KEY = os.environ.get("SHODAN_API_KEY")
print(f"[blue]API key:[/blue][i]{SHODAN_API_KEY}[/i]")
api = shodan.Shodan(SHODAN_API_KEY)
results = api.search("webcams")

for result in results["matches"]:
    if "MJPG-streamer" in result["data"]:
        url = f"http://{result['ip_str']}:{result['port']}"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                print(
                    f"[link={url}][i][green]{result['ip_str']}[/green]:[red]{result['port']}[/red][/link]"
                )
        except:
            continue
