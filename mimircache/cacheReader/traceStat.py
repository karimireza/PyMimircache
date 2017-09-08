# coding=utf-8


"""
this module provides the stat of the trace
"""

from pprint import pformat
from collections import defaultdict
from mimircache.utils.printing import *


class traceStat:
    """
    this class provides stat calculation for a given trace
    """
    def __init__(self, reader, top_N_popular=8):
        self.reader = reader
        self.top_N_popular = top_N_popular
        # stat data representation:
        #       0:  not initialized,
        #       -1: error while obtaining data

        self.num_of_requests = 0
        self.num_of_uniq_obj = 0
        self.cold_miss_ratio = 0

        self.top_N_popular_obj = []
        self.num_of_obj_with_freq_1 = 0
        self.freq_mean = 0
        self.time_span = 0

        # self.freq_median = 0
        # self.freq_mode = 0

        self._calculate()


    def _calculate(self):
        """
        calculate all the stat using the reader
        :return:
        """
        d = defaultdict(int)

        if self.reader.support_real_time:
            r = self.reader.read_time_request()
            assert r is not None, "failed to read time and request from reader"
            first_time_stamp = r[0]
            current_time_stamp = -1
            while r:
                d[r[1]] += 1
                current_time_stamp = r[0]
                r = self.reader.read_time_request()
            last_time_stamp = current_time_stamp

            self.time_span = last_time_stamp - first_time_stamp

        else:
            for i in self.reader:
                d[i] += 1

        self.reader.reset()

        self.num_of_uniq_obj = len(d)
        for _, v in d.items():
            self.num_of_requests += v

        self.cold_miss_ratio = self.num_of_uniq_obj/ (float) (self.num_of_requests)

        # l is a list of (obj, freq) in descending order
        l = sorted(d.items(), key=lambda x: x[1], reverse=True)
        self.top_N_popular_obj = l[:self.top_N_popular]
        for i in range(len(l)-1, -1, -1):
            if l[i][1] == 1:
                self.num_of_obj_with_freq_1 += 1
            else:
                break
        self.freq_mean = self.num_of_requests / (float) (self.num_of_uniq_obj)






    def get_stat(self, return_format="str"):
        """
        return stat in the format of string or tuple
        :param return_format:
        :return:
        """

        s = "number of requests: {}\nnumber of uniq obj/blocks: {}\n" \
            "cold miss ratio: {:.4f}\ntop N popular (obj, num of requests): \n{}\n" \
            "number of obj/block accessed only once: {}\n" \
            "frequency mean: {:.2f}\n{}".format(self.num_of_requests, self.num_of_uniq_obj,
                                                self.cold_miss_ratio,
                                                pformat(self.top_N_popular_obj),
                                                self.num_of_obj_with_freq_1,
                                                self.freq_mean,
                                                "time span: {}".format(self.time_span) if self.time_span else "")

        if return_format == "str":
            return s

        elif return_format == "tuple":
            return (self.num_of_requests, self.num_of_uniq_obj, self.cold_miss_ratio, self.top_N_popular_obj,
                    self.num_of_obj_with_freq_1, self.freq_mean, self.time_span)

        elif return_format == "dict":
            d = self.__dict__.copy()
            del d["top_N_popular"]
            return d

        else:
            WARNING("unknown return format, return string instead")
            return s


    def __repr__(self):
        return self.get_stat()


    def __str__(self):
        return self.get_stat()


if __name__ == "__main__":
    from mimircache import *
    reader = vscsiReader("../data/trace.vscsi")
    print(traceStat(reader).get_stat(return_format="dict"))