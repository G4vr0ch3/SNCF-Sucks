#!/usr/bin/env python3

import json
import time
import urllib.request as request
from datetime import datetime, timedelta


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

    info('Retrieving data disruption count...')

    try :
        res = request.urlopen(req)
    except :
        fail('Request failed.')
        exit()

    info('Fetching data...')
    fetch = json.loads(res.read())

    if fetch == '': fail('Data fetch failed.'); exit()

    count = fetch["page"]['fullCount']

    info('Retrived ' + str(count) + ' disruptions.')

    return count


def fetch():

    global_data = []

    info('Building request...')

    api = "https://api.airfranceklm.com/"
    dataset = "opendata/flightstatus"

    yday = datetime.now() - timedelta(days=1)
    tday = datetime.now()

    args = "?startRange={}Z&endRange={}Z&operatingAirlineCode=AF".format(yday.strftime("%Y-%m-%dT%H:%M:%S"), tday.strftime("%Y-%m-%dT%H:%M:%S"))

    url = api+dataset+args

    glob_dis_count = get_pages(url)

    pages = glob_dis_count//100 + 1

    info('Going through ' + str(pages) + ' pages of data. Fasten your seatbelts.')

    begin = time.time()

    for page_number in range(pages):

        info('Going through page n°' + str(page_number))

        args += "pageSize=100&pageNumber={}".format(page_number)
        req = request.Request(url, headers=header)

        try :
            res = request.urlopen(req)

            fetch = json.loads(res.read())

            if fetch == '':
                fail('Data fetch failed.')
            else:
                AF_data = get_AF(fetch)
                global_data.append(AF_data)
                success('Fetch n°' + str(page_number) + ' complete')

        except :
            fail('Request failed.')

    elapsed = time.time() - begin

    success('Data fetched in ' + str(elapsed) + 'ms')

    return global_data, pages

def get_AF(fetch):

    AF_flights = []

    flights = fetch["operationalFlights"]

    for flight in flights:
        # The "AF" check is useless because of the improved query. However, still need a check to take in account completed flights only
        if flight["airline"]["code"] == "AF" and flight["flightLegs"][0]["completionPercentage"] == "100" :
            AF_flights.append(flight)
        else:
            pass

    info('Retrieved ' + str(len(AF_flights)) + ' AirFrance flights.')

    return AF_flights

def dissect_data(fetch):

    raw, pages = fetch[0], fetch[1]

    it, total_delay, deleted, trip_delays, processed_flights, failure = 0, 0, 0, [], [], False

    info('Analyzing data...')

    begin = time.time()

    for page in range(pages):

        for flight in raw[page]:

            trip_delays = []

            if flight["flightNumber"] in processed_flights:
                pass

            else:

                processed_flights.append(flight["flightNumber"])

                flight_data = flight["flightLegs"]

                for data in flight_data:
                    if data["status"] == "C":
                        deleted += 1

                    elif "arrivalDateTimeDifference" in data:
                        it += 1

                        adelay = data["arrivalDateTimeDifference"]

                        if adelay == "PT0S" or "-" in adelay:
                            trip_delays.append(0)
                        else:
                            adelay = int(''.join(''.join(''.join(adelay.split("PT")).split("H")).split("M")))
                            trip_delays.append((adelay//100)*3600 + (adelay%100)*60)

                    if trip_delays == [0]:
                        # Means the plane was not late in the end
                        it -= 1

                if max(trip_delays) > 0 :
                    total_delay += max(trip_delays)

    elapsed = time.time() - begin

    success('Data analyze completed in ' + str(elapsed) + 'ms')

    return total_delay, deleted, failure, it

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
            print('[-] \033[1m In 24 hours, ', count, ' journeys were disrupted for a total of ', days, ' days, ', hours, ' hours and ', min, ' minutes. ', deleted, ' planes were deleted.' )
        except Exception as e:
            fail('Resluts failed sith error : ' + str(e))

    else:
        print('[-] \033[1m In 24 hours, ', count, ' journeys were disrupted for a total of ', days, ' days, ', hours, ' hours and ', min, ' minutes. ', deleted, ' planes were deleted.' )



################################################################################


if __name__ == "__main__":
    from prints import *
    from secrets import *


    header = { 'Accept-Language' : 'en-GB', 'Accept' : 'application/hal+json', 'Api-Key' : airfrance_secret } #W00w that's bad security...


    fetch = fetch()
    data = dissect_data(fetch)
    result(data)

else:
    from .prints import *
    from .secrets import *


    header = { 'Accept-Language' : 'en-GB', 'Accept' : 'application/hal+json', 'Api-Key' : airfrance_secret } #W00w that's bad security...



################################################################################
