import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json


def parse_tz(tzstr):
    sign = -1 + (tzstr[0] == "+") * 2  # 1 if timezone is positive, -1 if timezone is negative
    tzstr = tzstr[1:]
    hour, minute = tzstr.split(":")
    hour = int(hour) * sign
    minute = int(minute) * sign
    dt = timedelta(hours=hour, minutes=minute)
    return timezone(dt)


def get_time(tzstr):
    timeZone = parse_tz(tzstr)
    curTime = datetime.now(tz=timeZone)
    return curTime.hour, curTime.minute


class Locater:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://geo.ipify.org/api/v1"
        self.directory = Path(__file__).parent
        self.cache_path = self.directory / "geoip_cache.json"
        self.cache = {}
        self.load_cache()
        self.api_cnt = 0

    def load_cache(self):
        if not self.cache_path.is_file():
            with open(self.cache_path, 'w') as f:
                json.dump(dict(), f)
        with open(self.cache_path, "r") as f:
            self.cache = json.load(f)

    def store_cache(self):
        with open(self.cache_path, 'w') as f:
            json.dump(self.cache, f)

    def locate(self, ip):
        if ip in self.cache:
            t = self.cache[ip]
            country = t['country']
            region = t['region']
            hour = t['hour']
            minute = t['minute']
        else:
            data = dict()
            data['apiKey'] = self.api_key
            data['ipAddress'] = ip
            r = requests.get(self.url, params=data)
            self.api_cnt += 1
            res = r.json()
            country = res['location']['country']
            region = res['location']['region']
            timeZone = res['location']['timezone']
            hour, minute = get_time(timeZone)
            self.cache[ip] = dict()
            self.cache[ip]['country'] = country
            self.cache[ip]['hour'] = hour
            self.cache[ip]['region'] = region
            self.cache[ip]['minute'] = minute
            self.store_cache()
        return country, region, hour, minute
