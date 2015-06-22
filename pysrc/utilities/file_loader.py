"""
Creates an instance of a file loader. Takes in a file and parses it into a stream of experience
where each step is a dictionary in an array. The dictionary keys are as specified in the header of
the file.
"""
__author__ = 'alex'


class FileLoader(object):

    def __init__(self, file_loc):
        """Initializes a file-loader given a file-location"""
        f = open(file_loc, 'r')                 # open the file for reading
        self.data_stream = []                   # this is where we store the stream of experience
        self.elements = f.readline().rstrip().split(',')  # extracts the header of the file
        for line in f:
            vals = line.rstrip().split(',')              # separate all the values in an observation
            self.data_stream.append(dict([(self.elements[i], float(vals[i])) for i in range(len(vals))]))

    def step(self):
        """If there are still observations, returns the next observation. Else returns None"""
        if len(self.data_stream) > 0:           # while we still have experience
            return self.data_stream.pop()       # return the next observation
        else:                                   # otherwise we have nothing left
            return None                         # so return None.