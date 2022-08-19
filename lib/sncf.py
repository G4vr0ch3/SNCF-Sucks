#!/usr/bin/env python3

import json
import time
import urllib.request as request
from datetime import datetime, timedelta


################################################################################
#                                    _____ _   _  _____ ______                 #
#        _____                      / ____| \ | |/ ____|  ____|                #
#    ___ |[]|_n__n_I_c             | (___ |  \| | |    | |__                   #
#   |___||__|###|____}              \___ \| . ` | |    |  __|                  #
#    O-O--O-O+++--O-O               ____) | |\  | |____| |                     #
#                                  |_____/|_| \_|\_____|_|                     #
#                                                                              #
################################################################################





def fetch():
    info('Building request...')

    api = "https://api.sncf.com/v1/"
    dataset = "coverage/sncf/disruptions/"

    yday = datetime.now() - timedelta(days=1)
    tday = datetime.now()

    args = "?since={}&until={}".format(yday.strftime("%Y%m%dT%H%M%S"), tday.strftime("%Y%m%dT%H%M%S"))

    url_ = api+dataset+args

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
    info(str(dis_count) + ' disruptions found.')

    # Fetching all disruptions

    fetch = []

    pages = dis_count // 1000
    begin = time.time()

    info('Going through {} pages of data. Go grab a 3$ 33cl bottle at the bar !'.format(pages + 1))

    for page_number in range(pages + 1):
        infor('Fetching disruptions on page {}/{}...'.format(page_number + 1, pages + 1))

        url = api+dataset+args+"&count=1000&start_page={}".format(page_number)

        req = request.Request(url, headers=header)

        try :
            res = request.urlopen(req)
        except :
            print()
            fail('Request failed.')
            exit()

        fetch_ = json.loads(res.read())

        for disruption in fetch_["disruptions"]:
            fetch.append(disruption)

    if fetch == []:
        print()
        fail('Data fetch failed.')
        print(fetch, url)
        exit()
    else:
        elapsed = time.time() - begin
        print()
        success('Data fetched in ' + str(round(elapsed, 2)) + 's')

    return fetch





def dissect_data(raw):

    pd, it, jt, total_delay, deleted, failure, uids = 0, 0, 0, 0, 0, False, []

    info('Analyzing data...')

    begin = time.time()

    for disruption in raw :

        uid = disruption["disruption_id"]

        if uid in uids:
            pass

        else:
            uids.append(uid)
            objects = disruption["impacted_objects"]
            pd += 1
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
                            # Unusable data
                            it -= 1
                        else:
                            # Missing data
                            pass

                    if deleted_stop:
                        deleted += 1

                except Exception as e:
                    if 'impacted_stops' not in str(e): failure = True; fail('Failed with error :' + str(e) + ' | (item) : ' + str(item))

                # Keeping max delay of trip as delay
                total_delay += max(dlist)

    info('Retrieving global trip count ...')

    gcount = get_all_trips()

    elapsed = time.time() - begin

    success('Data analyze completed in ' + str(round(elapsed, 2)) + 's')
    return trip_data(total_delay, deleted, it, failure, gcount)





def result(data):

    secs, deleted, failure, it = data.duration_secs, data.deleted_count, data.data_corruption, data.dataset_size


    avg = convert((secs//it))
    delay = convert(secs)


    if failure :
        fail('Something bad happened...')
        try:
            print('[-] \033[1m In 24 hours, ', it, ' journeys were disrupted for a total of ', delay[2], ' days, ', delay[1], ' hours and ', delay[0], ' minutes, for an average delay of ', avg[2], ' days, ', avg[1], ' hours and ', avg[0], 'minutes. ', deleted, ' trains were deleted.' )
        except Exception as e:
            fail('Resluts failed with error : ' + str(e))

    else:
            print('[-] \033[1m In 24 hours, ', it, ' journeys were disrupted for a total of ', delay[2], ' days, ', delay[1], ' hours and ', delay[0], ' minutes, for an average delay of ', avg[2], ' days, ', avg[1], ' hours and ', avg[0], 'minutes. ', deleted, ' trains were deleted.' )





def convert(sec):
    min = (sec//60)%60
    hours = (sec-min*60)//3600
    days = hours//24
    hours -= days*24

    return (min, hours, days)





def fetch_type(raw):
    types = []
    for period in raw["disruptions"] :
        objects = period["impacted_objects"]
        for object in objects:
            pt = object["pt_object"]
            type = pt["trip"]["id"].split(":")[-1]
            if type not in types:
                types.append(type)
            else:
                pass

    return types





def get_all_trips():

    api = "https://api.sncf.com/v1/"
    dataset = "coverage/sncf/vehicle_journeys/"

    yday = datetime.now() - timedelta(days=1)
    tday = datetime.now()

    args = "?count=0&since={}&until={}".format(yday.strftime("%Y%m%dT%H%M%S"), tday.strftime("%Y%m%dT%H%M%S"))

    url_ = api+dataset+args

    req = request.Request(url_, headers=header)

    # Fething number of entries

    info('Sending request ...')
    try :
        res_ = request.urlopen(req)
    except :
        fail('Request failed.')
        exit()

    fetch_ = json.loads(res_.read())

    if fetch_ == '': fail('Data fetch failed.'); exit()

    dis_count = fetch_["pagination"]["total_result"]
    info(str(dis_count) + ' trips found.')

    return dis_count





################################################################################


if __name__ == "__main__":
    from prints import *
    from secrets import *
    from comparer import *


    header = { 'Authorization' : sncf_secret() } #W00w that's bad security...


    fetch = fetch()
    data = dissect_data(fetch)

    result(data)

#    print(fetch_type(fetch))

#    print(get_all_trips())

else:
    from .prints import *
    from .secrets import *
    from .comparer import *


    header = { 'Authorization' : sncf_secret() } #W00w that's bad security...



################################################################################
