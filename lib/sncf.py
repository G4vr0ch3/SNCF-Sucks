#!/usr/bin/env python3

import json
import urllib.request as request
from datetime import datetime, timedelta
from prints import success, info, warning, fail

pd, it, jt, total_delay, deleted, failure = 0, 0, 0, 0, 0, False

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
#args = "?since=20220806T210000&until=20220807T210000"

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
        dlist = [0]
        it+=1
        jt = 0
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

                    if datap == 2: warning('No usable data for stop n°' + str(jt) + ' for trip n°' + str(it))

                    delay = max(adelay, ddelay)

                    if delay == 0 and datap < 2 and jtem['departure_status'] != 'unchanged':
                        if jtem['arrival_status'] == 'added':
                            warning('Train delayed with no data')
                        else:
                            pass

                    if ddelay < 0:
                        fail('ddelay for n°' + str(jt) +' :\n')
                        warning(jtem)
                    elif adelay < 0:
                        fail('adelay for n°' + str(jt) +' :\n')
                        warning(jtem)
                    else:
                        pass

                    if delay>=0: dlist.append(delay)
                    else: fail(delay); warning(jtem);

                else:
                    info('Stop deleted for n°' + str(jt))
                    deleted += 1
                    jt += 1

        except Exception as e:
            if 'pt_object' not in item: failure = True; fail('Failed with error :' + str(e) + ' | (item) : ' + str(item))

        total_delay += max(dlist)

if failure :
    fail('Something bad happened...')
    try:
        result(it, total_delay, deleted)
    except Exception as e:
        fail('Resluts failed sith error : ' + str(e))

else:
    success('Success.')
    result(it, total_delay, deleted)
