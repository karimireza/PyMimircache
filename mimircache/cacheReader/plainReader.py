from mimircache.cacheReader.abstractReader import cacheReaderAbstract
import mimircache.c_cacheReader as c_cacheReader


class plainReader(cacheReaderAbstract):
    def __init__(self, file_loc, data_type='c', open_c_reader=True):
        super(plainReader, self).__init__(file_loc, data_type)
        self.trace_file = open(file_loc, 'r')
        if open_c_reader:
            self.cReader = c_cacheReader.setup_reader(file_loc, 'p', data_type=data_type)

    def read_one_element(self):
        super().read_one_element()
        line = self.trace_file.readline()
        if line:
            return line.strip()
        else:
            return None

    def __next__(self):  # Python 3
        super().__next__()
        element = self.trace_file.readline().strip()
        if element:
            return element
        else:
            raise StopIteration

    def __repr__(self):
        return "basic cache reader, cache trace separated by line, %s" % super().__repr__()
