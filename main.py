#!/usr/bin/env python3

from lib.prints import *
from lib import sncf

def main():
    info('Computing SNCF delay')
    fetch = sncf.fetch()
    data = sncf.dissect_data(fetch)
    sncf.result(data)

if __name__ == "__main__":
    main()
