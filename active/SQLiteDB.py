import sqlite3
import datetime as dt

str_or_None = lambda v: v if v is None else str(v)

class SQLiteDB:

    #############################################################################
    #   Utility methods:                                                        #
    #       * __init__                                                          #
    #       * connect                                                           #
    #       * set                                                               #
    #       * get                                                               #
    #                                                                           #
    #  str(query) is used in set and get to enable string-interpretable objects #
    #  to be used as queries (sqlite3 doesn't duck-type its input here).        #
    #############################################################################

    def __init__( self, *args ):
        self.file = self.DEFAULT_DB if len(args) == 0 else args[0]

    def connect( self):
        return sqlite3.connect( self.file)

    def set( self, query, *vals):
        conn = self.connect()
        with conn:
            conn.execute( str(query), tuple( map( str_or_None, vals)) )
        conn.close()
        return True

    def get( self, query, *vals, single=False):
        #   Any single-item fetch values are converted to just the item.
        #      e.g.: ( (1), (2) ) is returned as (1, 2)
        #
        conn = self.connect()
        if single:
            return_item = conn.cursor().execute( str(query), tuple( map( str_or_None, vals))).fetchone()
            if hasattr( return_item, "__iter__") and len( return_item) == 1:
                return_item = return_item[0]
        else:
            return_item = conn.cursor().execute( str(query), tuple( map( str_or_None, vals))).fetchall()
            if hasattr( return_item, "__iter__") and return_item and len( return_item[0]) == 1:
                return_item = *( tup[0] for tup in return_item ),
        conn.close()
        return return_item

    #########################################################
    #                                                       #
    #   Build and Execute SQL Queries                       #
    #       *   select (and select_one)                     #
    #       *   insert                                      #
    #   The others I don't use enough to implemenet here.   #
    #                                                       #
    #########################################################

    @staticmethod
    def _build_select_query( *args, **dd):
        cols, vals = zip( *dd.items()) if dd else (list(), list())
        table_name = args[-1]
        attrs      = args[:-1] if len(args) > 1 else '*'
        query      = f"SELECT {','.join( attrs)} FROM {table_name}"
        if dd:
            query     += f" WHERE "
            conditions = *( f"{col} = ?" for col in cols),
            query     += " AND ".join( conditions)
        return query, vals

    def select( self, *args, **dd):
        query, vals = self._build_select_query( *args, **dd)
        return self.get( query, *vals, single=False)

    def select_one( self, *args, **dd):
        query, vals = self._build_select_query( *args, **dd)
        return self.get( query, *vals, single=True)

    def insert( self, table_name, **dd):
        cols, vals = zip( *dd.items())
        QUERY      = f"INSERT INTO {table_name} ({','.join(cols)}) VALUES ({','.join( ['?']*len(cols))})"
        self.set( QUERY, *vals)

    ############################################################
    #                                                          #
    #   Other:                                                 #
    #       *   now (property) - the time as YYYY-MM-DD HH:MM. #
    #                                                          #
    ############################################################

    @property
    def now( self):
        return dt.datetime.today().strftime( "%Y-%m-%d %H:%M")
