#!/usr/bin/env python3


class trip_data:

    def __init__(self, duration_secs = 0, deleted_count = 0, dataset_size = 0, data_corruption = False, global_data_count = 0):
        self.duration_secs = duration_secs
        self.deleted_count = deleted_count
        self.dataset_size = dataset_size
        self.data_corruption = data_corruption
        self.global_data_count = global_data_count

def percent(sncf, af):

    sncf_perc = (sncf.dataset_size/sncf.global_data_count)//0.01
    af_perc = (af.dataset_size[0]/af.global_data_count)//0.01

    return sncf_perc, af_perc


def compare_numb(sncf, af):

    if sncf.dataset_size > af.dataset_size[0] :

        print('[-] \033[1m In the last 24 hours, the SNCF was ', int(sncf.dataset_size/af.dataset_size[0]), ' times more often late than AirFrance for ', round((sncf.duration_secs/af.duration_secs), 1), ' times as long.')

    #try:
        perc = percent(sncf, af)
        print('[-] \033[1m The SNCF was late for ', perc[0], '% of their trips and AirFrance for ', perc[1], '% of theirs.')
        #except:
        #    pass

        print('SNCF Sucks !')

    else:

        print('[-] \033[1m In the last 24 hours, AirFrance was ', int(af.dataset_size/sncf.dataset_size[0]), ' times more often late than the SNCF for ', round((af.duration_secs/sncf.duration_secs), 1), ' times as long.')

        try:
            perc = percent(sncf, af)
            print('[-] \033[1m AirFrance was late for ', perc[1], '% of their trips and the SNCF for ', perc[0], '% of theirs.')
        except:
            pass

        print('SNCF Sucks anyway !')
