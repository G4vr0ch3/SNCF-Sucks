#!/usr/bin/env python3

from pyfiglet import figlet_format as pfg
from lib.prints import *
from lib import sncf, airfrance



################################################################################
#           _____ _   _  _____ ______    _____            _                    #
#          / ____| \ | |/ ____|  ____|  / ____|          | |                   #
#         | (___ |  \| | |    | |__    | (___  _   _  ___| | _____             #
#          \___ \| . ` | |    |  __|    \___ \| | | |/ __| |/ / __|            #
#          ____) | |\  | |____| |       ____) | |_| | (__|   <\__ \            #
#         |_____/|_| \_|\_____|_|      |_____/ \__,_|\___|_|\_\___/            #
#                                                                              #
################################################################################




def main():

    print(pfg('SNCF'))

    info('Computing SNCF delay')
    sncf_fetch = sncf.fetch()
    sncf_delay = sncf.dissect_data(sncf_fetch)

    print('\n\n\n')

    print(pfg('AirFrance'))

    info('Computing AirFrance delay')
    airfrance_fetch = airfrance.fetch()
    airfrance_delay = airfrance.dissect_data(airfrance_fetch)

    print('\n\n\n')

    sncf.result(sncf_delay)

    airfrance.result(airfrance_delay)

if __name__ == "__main__":
    main()
