#!/usr/bin/env python3

import json
import time

import urllib.request as request

from datetime import datetime, timedelta
from PetitPrinc3.libs.spinner import spinner
from PetitPrinc3.libs.prints import *



################################################################################
#           _                   _      ______                                  #
#          -\`\           /\   (_)    |  ____|                                 #
#     |\ ____\_\__       /  \   _ _ __| |__ _ __ __ _ _ __   ___ ___           #
#   -=\c`""""""" "`)    / /\ \ | | '__|  __| '__/ _` | '_ \ / __/ _ \          #
#      `~~~~~/ /~~`    / ____ \| | |  | |  | | | (_| | | | | (_|  __/          #
#         -=/ /       /_/    \_\_|_|  |_|  |_|  \__,_|_| |_|\___\___|          #
#          '-'                                                                 #
################################################################################



def get_pages(base_url):

    url = base_url + "&pageSize=1"

    req = request.Request(url, headers=header)

    info('Retrieving data count...')

    try :
        res = request.urlopen(req)
    except :
        fail('Request failed.')
        exit()

    info('Fetching data...')
    fetch = json.loads(res.read())

    if fetch == '': fail('Data fetch failed.'); exit()

    count = fetch["page"]['fullCount']

    info('Retrived ' + str(count) + ' flights carried by AirFrance.')

    return count





def fetch():

    global_data = []
    effective_count = 0

    info('Building request...')

    api = "https://api.airfranceklm.com/"
    dataset = "opendata/flightstatus"

    yday = datetime.now() - timedelta(days=1)
    tday = datetime.now()

    args = "?startRange={}Z&endRange={}Z&operatingAirlineCode=AF".format(yday.strftime("%Y-%m-%dT%H:%M:%S"), tday.strftime("%Y-%m-%dT%H:%M:%S"))

    url = api+dataset+args

    glob_dis_count = get_pages(url)


    if (glob_dis_count%100) > 0 :
        pages = glob_dis_count//100
    else:
        pages = glob_dis_count//100


    info('Going through ' + str(pages + 1) + ' pages of data. Fasten your seatbelts.')

    begin = time.time()

    for page_number in range(pages + 1):

        with spinner('Going through page ' + str(page_number + 1) + '/' + str(pages + 1) + '...'):

            url = api + dataset + args + "&pageSize=100&pageNumber={}".format(page_number)

            req = request.Request(url, headers=header)

            try :
                res = request.urlopen(req)

                fetch = json.loads(res.read())

                if fetch == '':
                    print()
                    fail('Data fetch failed.')
                else:
                    AF_data = get_AF(fetch)
                    global_data.append(AF_data)
                    effective_count += 1

            except :
                print()
                fail('Request failed.')

    elapsed = time.time() - begin

    print()
    success('Data fetched in ' + str(round(elapsed, 2)) + 's')

    return global_data, effective_count





def get_AF(fetch):

    AF_flights = []
    AF_count = 0

    flights = fetch["operationalFlights"]

    for flight in flights:
        # The "AF" check is useless because of the improved query. However, still need a check to take in account completed flights only
        if flight["flightLegs"][0]["completionPercentage"] == "100" :
            AF_flights.append(flight)
            AF_count += len(flight["flightLegs"])
        else:
            pass

    return AF_flights





def dissect_data(fetch):

    raw, pages = fetch[0], fetch[1]

    it, jt, total_delay, deleted, trip_delays, processed_flights, failure = 0, 0, 0, 0, [], [], False

    info('Analyzing data...')

    begin = time.time()

    for page in range(pages):

        for flight in raw[page]:

            trip_delays = [0]
            nat = False

            if flight["flightNumber"] in processed_flights:
                pass

            else:

                processed_flights.append(flight["flightNumber"])

                flight_data = flight["flightLegs"]

                for data in flight_data:

                    if data["status"] == "C":
                        deleted += 1

                    elif "arrivalDateTimeDifference" in data:

                        adelay = data["arrivalDateTimeDifference"]

                        if adelay == "PT0S" or "-" in adelay:
                            pass
                        else:
                            adelay = int(''.join(''.join(''.join(adelay.split("PT")).split("H")).split("M")))
                            trip_delays.append((adelay//100)*3600 + (adelay%100)*60)

                    if data["departureInformation"]["airport"]["city"]["country"]["code"] == "FR" and data["arrivalInformation"]["airport"]["city"]["country"]["code"] == "FR":
                        nat = True


                if max(trip_delays) > 0 :
                    total_delay += max(trip_delays)

                    if nat:
                        jt += 1

                    it += 1


    elapsed = time.time() - begin

    success('Data analyze completed in ' + str(round(elapsed, 2)) + 's')
    success('Went through ' + str(len(processed_flights)) + ' flights.')

    return trip_data(total_delay, deleted, (it, jt), failure, len(processed_flights))





def result(data):

    secs, deleted, failure, it, nat = data.duration_secs, data.deleted_count, data.data_corruption, data.dataset_size[0], data.dataset_size[1]


    avg = convert((secs//it))
    delay = convert(secs)


    if failure :
        fail('Something bad happened...')
        try:
            print('[-] \033[1m In 24 hours, ', it, ' journeys including ' + str(nat) + ' national flights were disrupted for a total of ', delay[2], ' days, ', delay[1], ' hours and ', delay[0], ' minutes, for an average delay of ', avg[2], ' days, ', avg[1], ' hours and ', avg[0], 'minutes. ', deleted, ' planes were deleted.' )
        except Exception as e:
            fail('Resluts failed with error : ' + str(e))

    else:
            print('[-] \033[1m In 24 hours, ', it, ' journeys including ' + str(nat) + ' national flights were disrupted for a total of ', delay[2], ' days, ', delay[1], ' hours and ', delay[0], ' minutes, for an average delay of ', avg[2], ' days, ', avg[1], ' hours and ', avg[0], 'minutes. ', deleted, ' planes were deleted.' )





def convert(sec):
    min = (sec//60)%60
    hours = (sec-min*60)//3600
    days = hours//24
    hours -= days*24

    return (min, hours, days)





################################################################################


if __name__ == "__main__":
    from prints import *
    from secrets import *
    from comparer import *


    header = { 'Accept-Language' : 'en-GB', 'Accept' : 'application/hal+json', 'Api-Key' : airfrance_secret() } #W00w that's bad security...


    fetch = fetch()
    data = dissect_data(fetch)
    result(data)

else:
    from .prints import *
    from .secrets import *
    from .comparer import *


    header = { 'Accept-Language' : 'en-GB', 'Accept' : 'application/hal+json', 'Api-Key' : airfrance_secret() } #W00w that's bad security...



################################################################################
