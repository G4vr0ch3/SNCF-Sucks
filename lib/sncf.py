import json
import urllib.request as request
from datetime import datetime, timedelta


def info(text):
    print('[*] \033[96m',text, '\033[0m')

def fail(text):
    print('[!] \033[91m',text, '\033[0m')

def success(text):
    print('[+] \033[92m',text, '\033[0m')

def result(count, delay):
    print('[-] \033[1m\033[93m In 24 hours, ', count, ' journeys were disrupted for a total of ', delay//60, ' hours and ', delay%60, ' minutes. SNCF Sucks.' )

info('Building request...')

api = "https://api.sncf.com/v1/"
dataset = "coverage/sncf/disruptions/"

day = datetime.now() - timedelta(days=1)

#args = "?since={}".format(day.strftime("%Y%m%d%H%M%S"))
args = "?since=20220804T0000&until=20220805T0000"

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

pd, it, tot, failure = 0, 0, 0, False

info('Analyzing data...')
for period in fetch["disruptions"] :
    parent = period["impacted_objects"][0]
    print(parent)
    pd += 1
    for item in parent:
        it += 1
        try:
            data = item["impacted_stops"][0]
            finaltime = int(data["amended_arrival_time"])
            try:
                basetime = int(data["base_arrival_time"])
                delay = finaltime - basetime
                if delay == 0: info(item)
            except:
                delay = finaltime

            tot += (delay//100 - delay//10000) + (delay//10000)*60
            info('Delay n°' + str(it) + ' : ' + str(delay))

        except Exception as e:
            if item != 'pt_object': failure = True; fail('Failed with error :' + str(e) + ' | (item) : ' + item)

if failure :
    fail('Something bad happened...')
    try:
        result(it, delay)
    except:
        pass

else:
    success('Success.')
    result(it, delay)
