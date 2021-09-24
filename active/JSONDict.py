import collections.abc
import json
import pathlib

class CommonMethodsMixin( collections.abc.Hashable):
    def new_file( self):
        raise NotImplementedError( "JSONDict classes need to implement this.")

    def __init__(self, path):
        if not isinstance( path,  pathlib.PurePath):
            raise ValueError( "This class must be initialized with a pathlib.Path object.")
        self.path = path

    @property
    def as_json( self):
        if not self.path.exists:
            return "{}"
        with open( self.path) as fh:
            return json.dumps( json.load( fh), indent=6 )

    def __getitem__( self, item):
        if not self.path.exists():
            raise KeyError( f"No file exists at: {self.path}")
        with open( self.path) as fh:
            return json.load( fh)[ item]

    def __iter__( self):
        if not self.path.exists():
            return iter( list())
        with open( self.path) as fh:
            return iter( json.load( fh))

    def __len__( self):
        if not self.path.exists():
            return 0
        with open( self.path) as fh:
            return len( json.load( fh))

    def __eq__( self, other):
        return isinstance( other, type(self)) and self.path == other.path

    def __hash__( self):
        return hash( str(self.path))

class ReadOnlyJSONDict( CommonMethodsMixin, collections.abc.Mapping):
    def new_file( self):
        raise TypeError( f"{type(self).__name__} cannot create a new file.")

class JSONDict( CommonMethodsMixin, collections.abc.MutableMapping):
    def new_file( self):
        with open( self.path, 'w') as fh:
            fh.write( "{}")

    def __setitem__( self, key, value):
        if not self.path.exists():
            self.new_file()
        with open( self.path, 'r') as fh:
            data = json.load( fh)
        data[ key] = value
        with open( self.path, 'w') as fh:
            json.dump( data, fh, indent=6)

    def __delitem__( self, key):
        if not self.path.exists():
            self.new_file()
        with open( self.path, 'r') as fh:
            data = json.load( fh)
        del data[ key]
        with open( self.path, 'w') as fh:
            json.dump( data, fh, indent=6)
