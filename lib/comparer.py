#!/usr/bin/env python3


class trip_data:

    def __init__(self, duration_secs = 0, deleted_count = 0, dataset_size = 0, data_corruption = False, global_data_count = 0):
        self.duration_secs = duration_secs
        self.deleted_count = deleted_count
        self.dataset_size = dataset_size
        self.data_corruption = data_corruption
        self.global_data_count = global_data_count


def compare_numb(sncf, af):

    if sncf.dataset_size > af.dataset_size[0] :

        print('[-] \033[1m In the last 24 hours, the SNCF was ', int(sncf.dataset_size/af.dataset_size[0]), ' times more late than AirFrance for ', sncf.duration_secs/af.duration_secs, ' times as long.')

    else:

        print('[-] \033[1m In the last 24 hours, AirFrance was ', int(af.dataset_size/sncf.dataset_size[0]), ' times more late than the SNCF for ', af.duration_secs/sncf.duration_secs, ' times as long.')
