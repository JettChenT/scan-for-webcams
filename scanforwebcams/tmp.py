from datetime import datetime,timedelta,timezone

def parse_tz(tzstr):
	sign = -1+(tzstr[0]=="+")*2 # 1 if timezone is positive, -1 if timezone is negative
	tzstr = tzstr[1:]
	hour,minute = tzstr.split(":")
	hour = int(hour)*sign
	minute = int(minute)*sign
	dt = timedelta(hours=hour,minutes=minute)
	return timezone(dt)
	

timeZone = parse_tz("+8:00")
curTime = datetime.now(tz=timeZone)
print(curTime.hour,curTime.minute)