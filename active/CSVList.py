import collections.abc
import csv

class CSVList( collections.abc.MutableSequence):
    def __init__( self, path):
        self.path = path

    def __getitem__( self, i):
        return self.read_tuples()[i]

    def __setitem__( self, item, value):
        data = self.read_tuples()
        data[ item] = value
        self.write_tuples( data)

    def __delitem__( self, i):
        data = self.read_tuples()
        del data[ i]
        self.write_tuples( data)

    def __len__( self):
        return len( self.read_tuples())

    def insert( self, i, item):
        data = self.read_tuples()
        data.insert( i, item)
        self.write_tuples( data)

    def read_tuples( self):
        if not self.path.exists():
            self.path.touch()
        with self.path.open( 'r') as fh:
            return [tuple(row) for row in csv.reader( fh) if len(row) > 0]

    def write_tuples( self, tuples):
        with self.path.open( 'w') as fh:
            for tuple in tuples:
                if isinstance( tuple, str):
                    tuple = (tuple,)
                csv.writer( fh).writerow( tuple)
