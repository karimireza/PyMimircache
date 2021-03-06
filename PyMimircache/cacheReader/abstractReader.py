# coding=utf-8
"""
    reader interface

    Author: Jason Yang <peter.waynechina@gmail.com> 2016/06

"""

import abc
import os
from collections import defaultdict
from PyMimircache.const import ALLOW_C_MIMIRCACHE
from multiprocessing import Manager, Lock

if ALLOW_C_MIMIRCACHE:
    import PyMimircache.CMimircache.CacheReader as c_cacheReader


class AbstractReader(metaclass=abc.ABCMeta):
    """
    reader interface

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, file_loc, data_type='c', block_unit_size=0,
                 disk_sector_size=0, open_c_reader=False, lock=None):
        """
        the initialization abstract function for cacheReaderAbstract
        :param file_loc:            location of the file
        :param data_type:           type of data(label), can be "l" for int/long, "c" for string
        :param block_unit_size:     block size for storage system, 0 when disabled
        :param disk_sector_size:    size of disk sector
        :param open_c_reader:       whether open c reader
        """

        self.file_loc = file_loc
        self.trace_file = None
        self.c_reader = None
        self.data_type = data_type
        self.block_unit_size = block_unit_size
        self.disk_sector_size = disk_sector_size
        self.open_c_reader = open_c_reader

        if self.disk_sector_size != 0:
            assert data_type == 'l', "block size option only support on block request(data type l)"
        assert (os.path.exists(file_loc)), "data file({}) does not exist".format(file_loc)

        self.support_real_time = False
        self.support_size = False
        self.already_load_rd = False

        self.lock = lock
        if self.lock is None:
            self._mp_manager = Manager()
            self.lock = self._mp_manager.Lock()

        self.counter = 0
        self.num_of_req = -1
        self.num_of_uniq_req = -1

    def reset(self):
        """
        reset the read location back to beginning, similar as rewind in POSIX
        """
        self.counter = 0
        self.trace_file.seek(0, 0)
        if self.c_reader:
            c_cacheReader.reset_reader(self.c_reader)

    def get_num_of_req(self):
        """
        count the number of requests in the trace, fast for binary type trace,
        for plain/csv type trace, this is slow
        :return: the number of requests in the trace
        """

        if self.num_of_req > 0:
            return self.num_of_req

        # clear before counting
        self.num_of_req = 0
        if self.c_reader:
            self.num_of_req = c_cacheReader.get_num_of_req(self.c_reader)
        else:
            while self.read_one_req() is not None:
                self.num_of_req += 1
        self.reset()

        return self.num_of_req

    def get_req_freq_distribution(self):
        """
        calculate the count for each block/obj
        :return: a dictionary mapping from block/ojb to count
        """

        d = defaultdict(int)
        for i in self:
            d[i] += 1
        self.reset()
        return d

    def get_num_of_uniq_req(self):
        """
        count the number of unique block/obj in the trace
        :return: the number of unique block/obj
        """

        if self.num_of_uniq_req == -1:
            self.num_of_uniq_req = len(self.get_req_freq_distribution())
        return self.num_of_uniq_req

    def __iter__(self):
        return self

    # noinspection PyMissingOrEmptyDocstring
    def next(self):
        return self.__next__()

    def __len__(self):
        return self.get_num_of_req()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @abc.abstractclassmethod
    def read_one_req(self):
        """
        read one request, only return the label of the request
        :return:
        """
        pass

    @abc.abstractclassmethod
    def copy(self, open_c_reader=False):
        """
        reader a deep copy of current reader with everything reset to initial state,
        the returned reader should not interfere with current reader

        :param open_c_reader: whether open_c_reader_or_not, default not open
        :return: a copied reader
        """
        pass

    @abc.abstractclassmethod
    def get_params(self):
        """
        return all the parameters for this reader instance in a dictionary
        :return: a dictionary containing all parameters
        """
        pass

    def close(self):
        """
        close reader, this is used to close the c_reader, which will not be automatically closed
        :return:
        """
        try:
            if self is not None:
                if self.trace_file:
                    self.trace_file.close()
                    self.trace_file = None
                if self.c_reader and c_cacheReader is not None:
                    c_cacheReader.close_reader(self.c_reader)
                    self.c_reader = None
        except Exception as e:
            # return
            print("Exception during close reader: {}, ccacheReader={}".format(e, c_cacheReader))

    @abc.abstractmethod
    def __next__(self):  # Python 3
        self.counter += 1

    # @atexit.register
    def __del__(self):
        self.close()
