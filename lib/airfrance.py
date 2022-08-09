#!/usr/bin/env python3

import json
import urllib.request as request
from datetime import datetime, timedelta
from prints import *

def fetch():
    info('Building request...')

    api = "https://api.airfranceklm.com/"
    dataset = "opendata/flightstatus"

    yday = datetime.now() - timedelta(days=1)
    tday = datetime.now()

    args = "?startRange={}&endRange={}".format(yday.strftime("%Y-%m-%dT%H:%M:%S"), tday.strftime("%Y-%m-%dT%H:%M:%S"))

    url = api+dataset+args

    header = { "Accept-Language:en-GB", "Accept:application/hal+json", "Api-Key:****" } #W00w that's bad security...

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

def get_AF(fetch):

    AF_flights = []

    flights = fetch["operationalFlights"][0]

    for flight in flights:
        if flight["airline"]["code"] == "AF":
            AF_flights.append(flight)
        else:
            pass

    info('Retrieved ' + str(len(AF_flights)) + ' AirFrance flights.')

    return AF_flights

def dissect_data(raw):

    for flight in raw:
        flight_data = flight["flightLegs"]

        if flight_data["status"] == "C":
            deleted += 1

        else:
            
