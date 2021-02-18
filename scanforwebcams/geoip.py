import requests
from datetime import datetime,timedelta,timezone

def parse_tz(tzstr):
    sign = -1+(tzstr[0]=="+")*2 # 1 if timezone is positive, -1 if timezone is negative
    tzstr = tzstr[1:]
    hour,minute = tzstr.split(":")
    hour = int(hour)*sign
    minute = int(minute)*sign
    dt = timedelta(hours=hour,minutes=minute)
    return timezone(dt)

def get_time(tzstr):
    timeZone = parse_tz(tzstr)
    curTime = datetime.now(tz=timeZone)
    return curTime.hour, curTime.minute

class Locater:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://geo.ipify.org/api/v1"
    
    
    def locate(self, ip):
        data = dict()
        data['apiKey'] = self.api_key
        data['ipAddress'] = ip
        r = requests.get(self.url, params=data)
        res = r.json()
        country = res['location']['country']
        region = res['location']['region']
        timeZone = res['location']['timezone']
        hour,minute = get_time(timeZone)
        return country, region, hour, minute
