#!/usr/bin/env python3

import json
import urllib.request as request
from datetime import datetime, timedelta
from .prints import *


def fetch():
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

    if fetch == '': fail('Data fetch failed.'); exit()

    return fetch


def dissect_data(raw):

    pd, it, jt, total_delay, deleted, failure, UIDS = 0, 0, 0, 0, 0, False, []

    info('Analyzing data...')
    for period in raw["disruptions"] :
        objects = period["impacted_objects"]
        pd += 1
        UIDS.append(period["disruption_id"])
        for item in objects:
            dlist = [0]
            it+=1
            jt = 0
            try:
                data = item["impacted_stops"]
                miss_data, count_miss = False, 0
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

                        if datap == 2: miss_data = True; count_miss += 1

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
                        deleted += 1

                if miss_data:
                    if count_miss == jt :
                        fail('Unusable data for it n°' + str(it))
                    else:
                        warning('Missing data for it n°' + str(it))

            except Exception as e:
                if 'impacted_stops' not in str(e): failure = True; fail('Failed with error :' + str(e) + ' | (item) : ' + str(item))

            total_delay += max(dlist)

    return (total_delay, deleted, failure, UIDS)


def result(data):

    delay, deleted, failure, UIDS = data[0], data[1], data[2], data[3]

    count = len(set(UIDS))
    min = delay%60
    hours = delay//60
    days = hours//24
    hours -= days*24

    if failure :
        fail('Something bad happened...')
        try:
            print('[-] \033[1m\033[93m In 24 hours, ', count, ' journeys were disrupted for a total of ', days, ' days, ', hours, ' hours and ', min, ' minutes. ', deleted, ' trains were deleted. SNCF Sucks.' )
        except Exception as e:
            fail('Resluts failed sith error : ' + str(e))

    else:
        success('Success.')
        print('[-] \033[1m\033[93m In 24 hours, ', count, ' journeys were disrupted for a total of ', days, ' days, ', hours, ' hours and ', min, ' minutes. ', deleted, ' trains were deleted. SNCF Sucks.' )

if __name__ == "__main__":
    fetch = fetch()
    data = dissect_data(fetch)
    result(data)
