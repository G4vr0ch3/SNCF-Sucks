import json
import urllib.request as request
from datetime import datetime, timedelta

pd, it, jt, tot, deleted, failure = 0, 0, 0, 0, 0, False

def info(text):
    print('[*] \033[96m',text, '\033[0m')

def fail(text):
    print('[!] \033[91m',text, '\033[0m')

def success(text):
    print('[+] \033[92m',text, '\033[0m')

def warning(text):
    print('[+] \033[93m',text, '\033[0m')

def result(count, delay, deleted):
    min = delay%60
    hours = delay//60
    days = hours//24
    hours -= days*24
    print('[-] \033[1m\033[93m In 24 hours, ', count, ' journeys were disrupted for a total of ', days, ' days, ', hours, ' hours and ', min, ' minutes. ', deleted, ' trains were deleted. SNCF Sucks.' )

info('Building request...')

api = "https://api.sncf.com/v1/"
dataset = "coverage/sncf/disruptions/"

day = datetime.now() - timedelta(days=1)

args = "?since={}".format(day.strftime("%Y%m%d%H%M%S"))

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
                    adelay, ddelay, datap = 0, 0, 0
                    jt += 1
                    try:
                        afinaltime = int(jtem["amended_arrival_time"])
                        abasetime = int(jtem["base_arrival_time"])
                        if afinaltime < abasetime:
                            adelay = (afinaltime%100 + ((240000 - abasetime)%100) + ((afinaltime//100)%100)*60 + (((240000 - abasetime)//100)%100)*60 + (afinaltime//10000)*3600 + ((240000 - abasetime)//10000)*3600)
                        else:
                            adelay = (afinaltime%100 - abasetime%100) + ((afinaltime//100)%100 - (abasetime//100)%100)*60 + ((afinaltime//10000) - (abasetime//10000))*3600
                    except:
                        datap += 1
                    try:
                        dfinaltime = int(jtem["amended_departure_time"])
                        dbasetime = int(jtem["base_departure_time"])
                        if dfinaltime < dbasetime > 1:
                            ddelay = (dfinaltime%100 + ((240000 - dbasetime)%100) + ((dfinaltime//100)%100)*60 + (((240000 - dbasetime)//100)%100)*60 + (dfinaltime//10000)*3600 + ((240000 - dbasetime)//10000)*3600)
                        else:
                            ddelay = (dfinaltime%100 - dbasetime%100) + ((dfinaltime//100)%100 - (dbasetime//100)%100)*60 + ((dfinaltime//10000) - (dbasetime//10000))*3600
                    except:
                        datap += 1

                    if datap == 2: warning('No usable data for n°' + str(jt))

                    delay = max(adelay, ddelay)

                    if delay == 0 and jtem['departure_status'] != 'unchanged':
                        if jtem['arrival_status'] == 'added':
                            delay = int(tot//jt)
                        else:
                            jt -= 1

                    if ddelay < 0:
                        fail('ddelay for n°' + str(jt) +' :\n')
                        warning(jtem)
                    elif adelay < 0:
                        fail('adelay for n°' + str(jt) +' :\n')
                        warning(jtem)
                    else:
                        info('Arrival delay : ' + str(adelay))
                        info('Departure delay : ' + str(ddelay))

                    info('Delay n°' + str (jt) + ' : ' + str(delay//60) + ' minutes')
                    if delay>=0: tot += delay
                    else: fail(delay); warning(jtem);
                    warning('Cumulative delay : ' + str(tot))

                else:
                    info('Stop deleted for n°' + str(jt))
                    deleted += 1
                    jt += 1

        except Exception as e:
            if 'pt_object' not in item: failure = True; fail('Failed with error :' + str(e) + ' | (item) : ' + str(item))

if failure :
    fail('Something bad happened...')
    try:
        result(jt, delay, deleted)
    except Exception as e:
        fail('Resluts failed sith error : ' + str(e))

else:
    success('Success.')
    result(jt, delay, deleted)
