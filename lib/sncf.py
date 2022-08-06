import json
import urllib.request as request
from datetime import datetime, timedelta


def info(text):
    print('[*] \033[96m',text, '\033[0m')

def fail(text):
    print('[!] \033[91m',text, '\033[0m')

def success(text):
    print('[+] \033[92m',text, '\033[0m')

def warning(text):
    print('[+] \033[93m',text, '\033[0m')

def result(count, delay):
    min = delay%60
    hours = delay//60
    days = hours//24
    hours -= days*24
    weeks = days//7
    days -= weeks*7
    print('[-] \033[1m\033[93m In 24 hours, ', count, ' journeys were disrupted for a total of ', weeks, ' weeks, ', days, ' days, ', hours, ' hours and ', min, ' minutes. SNCF Sucks.' )

info('Building request...')

api = "https://api.sncf.com/v1/"
dataset = "coverage/sncf/disruptions/"

day = datetime.now() - timedelta(days=1)

args = "?since={}".format(day.strftime("%Y%m%d%H%M%S"))
#args = "?since=20220804T0000&until=20220805T0000&data_freshness=base_schedule"

url = api+dataset+args

header = { 'Authorization' : '<REDACTED>' } #W00w that's bad security...

req = request.Request(url, headers=header)

info('Sending request...')
try :
    res = request.urlopen(req)
except :
    fail('Request failed.')
    exit()

info('Fetching data...')
fetch = json.loads(res.read())

if fetch == '': fail('Data fetch failed.')

pd, it, jt, tot, failure = 0, 0, 0, 0, False

info('Analyzing data...')
for period in fetch["disruptions"] :
    objects = period["impacted_objects"]
    pd += 1
    for item in objects:
        it+=1
        try:
            data = item["impacted_stops"]
            for jtem in data:
                if jtem["arrival_status"] != "deleted":
                    adelay, ddelay = 0, 0
                    jt += 1
                    try:
                        afinaltime = int(jtem["amended_arrival_time"])
                        abasetime = int(jtem["base_arrival_time"])
                        if afinaltime//1000000 - abasetime//1000000 > 1:
                            adelay = (afinaltime%1000000 + (240000 - abasetime%1000000))
                        else:
                            adelay = (afinaltime - abasetime)
                        info('Arrival delay : ' + str(adelay))
                    except:
                        warning('Missing arrival data for n°' + str(it))
                    try:
                        dfinaltime = int(jtem["amended_departure_time"])
                        dbasetime = int(jtem["base_departure_time"])
                        if dfinaltime//1000000 - dbasetime//1000000 > 1:
                            ddelay = (dfinaltime%1000000 + (240000 - dbasetime%1000000))
                        else:
                            ddelay = (dfinaltime - dbasetime)
                        info('Departure delay : ' + str(ddelay))
                    except:
                        warning('Missing departure data for n°' + str(it))

                    delay = max(adelay, ddelay)
                    if delay == 0 and jtem['departure_status'] != 'unchanged': info(item)
                    delay = (delay//10000)*3600 + ((delay%10000)//100)*60 + delay%60
                    info('Delay n°' + str (jt) + ' : ' + str(delay*60) + 'minutes')
                    tot += delay
                    warning('Cumulative delay : ' + str(tot))

                else:
                    info('Stop deleted for n°' + str(jt))

        except Exception as e:
            if item != 'pt_object': failure = True; fail('Failed with error :' + str(e) + ' | (item) : ' + str(item))

if failure :
    fail('Something bad happened...')
    try:
        result(jt, delay)
    except:
        pass

else:
    success('Success.')
    result(jt, delay)
