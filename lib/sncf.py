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

    args = "?since={}".format(day.strftime("%Y%m%dT%H%M%S"))

    url_ = api+dataset+args

    header = { 'Authorization' : '***' } #W00w that's bad security...

    req = request.Request(url_, headers=header)

    # Fething number of entries

    info('Requesting disruption count...')
    try :
        res_ = request.urlopen(req)
    except :
        fail('Request failed.')
        exit()

    fetch_ = json.loads(res_.read())

    if fetch_ == '': fail('Data fetch failed.'); exit()

    dis_count = fetch_["pagination"]["total_result"]
    info(str(dis_count) + ' disruptions found')

    # Fetching all disruptions

    info('Fetching data...')

    args += "&count={}".format(dis_count)
    url = api+dataset+args

    req = request.Request(url, headers=header)

    info('Sending request...')
    try :
        res = request.urlopen(req)
    except :
        fail('Request failed.')
        exit()

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
            jt, deleted_stop = 0, False
            try:
                data = item["impacted_stops"]
                miss_data, count_miss = False, 0
                for jtem in data:
                    if jtem["arrival_status"] != "deleted":

                        # Computing delay at each stop
                        adelay, ddelay, datap = 0, 0, 0
                        jt += 1

                        # Final delay
                        try:
                            afinaltime = int(jtem["amended_arrival_time"])
                            abasetime = int(jtem["base_arrival_time"])
                            if afinaltime < abasetime:
                                adelay = (afinaltime%100 + ((240000 - abasetime)%100) + ((afinaltime//100)%100)*60 + (((240000 - abasetime)//100)%100)*60 + (afinaltime//10000)*3600 + ((240000 - abasetime)//10000)*3600)
                            else:
                                adelay = (afinaltime%100 - abasetime%100) + ((afinaltime//100)%100 - (abasetime//100)%100)*60 + ((afinaltime//10000) - (abasetime//10000))*3600
                        except:
                            datap += 1

                        # Delay on departure (unused)
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

                        delay = adelay

                        if delay == 0 and datap < 2 and jtem['departure_status'] != 'unchanged':
                            if jtem['arrival_status'] == 'added':
                                warning('Train delayed with no data')
                            else:
                                pass
                        else:
                            pass

                        # Delay checks
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

                        # Counting deleted trains
                        deleted_stop = True

                if miss_data:
                    if count_miss == jt :
                        fail('Unusable data for it n°' + str(it))
                        it -= 1
                    else:
                        warning('Missing data for it n°' + str(it))

                if deleted_stop:
                    deleted += 1

            except Exception as e:
                if 'impacted_stops' not in str(e): failure = True; fail('Failed with error :' + str(e) + ' | (item) : ' + str(item))

            #Keeping max delay of trip as delay
            total_delay += max(dlist)

    return (total_delay, deleted, failure, it)


def result(data):

    delay, deleted, failure, it = data[0], data[1], data[2], data[3]

    count = it
    min = (delay//60)%60
    hours = (delay-min*60)//3600
    days = hours//24
    hours -= days*24

    if failure :
        fail('Something bad happened...')
        try:
            print('[-] \033[1m In 24 hours, ', count, ' journeys were disrupted for a total of ', days, ' days, ', hours, ' hours and ', min, ' minutes. ', deleted, ' trains were deleted. SNCF Sucks.' )
        except Exception as e:
            fail('Resluts failed sith error : ' + str(e))

    else:
        success('Success.')
        print('[-] \033[1m In 24 hours, ', count, ' journeys were disrupted for a total of ', days, ' days, ', hours, ' hours and ', min, ' minutes. ', deleted, ' trains were deleted. SNCF Sucks.' )

if __name__ == "__main__":
    fetch = fetch()
    data = dissect_data(fetch)
    result(data)
