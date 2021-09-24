from pyutil.standard_import import *
import sqlite3

#############################################
#                                           #
#   SQL Statement Builders                  #
#   * Currently held in the BaseSQL Enum.   #
#                                           #
#############################################
def _build_select_statement( table_name, **kwargs):
    select_cols = ','.join( kwargs[ 'select_columns']) if 'select_columns' in kwargs else'*'
    query       = f"SELECT {select_cols} FROM {table_name}"
    condition   = ' AND '.join( [ f'{col}=?' for col in kwargs['condition_columns']] ) if 'condition_columns' in kwargs else ''
    ending      = " WHERE " + condition + ";" if condition else ";"
    return query + ending

def _build_insert_statement( table_name, **kwargs):
    if 'condition_columns' not in kwargs:
        raise ValueError( f"No condition columns for insert to {table_name}.")
    condition_columns = kwargs[ 'condition_columns']
    return f"INSERT INTO {table_name} ({','.join(condition_columns)}) VALUES ({','.join( ['?']*len(condition_columns))})"

def _build_delete_statement( table_name, **kwargs):
    if 'condition_columns' not in kwargs:
        raise ValueError( f"No condition columns for non-all delete statement from {table_name}.")
    columns = kwargs[ 'condition_columns']
    condition_columns = ' AND '.join( [ f'{col}=?' for col in kwargs['condition_columns']] ) if 'condition_columns' in kwargs else ''
    return f"DELETE FROM {table_name} WHERE {condition}"

@enum.unique
class BaseSQL( enum.Enum):
    INSERT = lambda table_name, **kwargs: _build_insert_statement( table_name, **kwargs)
    SELECT = lambda table_name, **kwargs: _build_select_statement( table_name, **kwargs)
    DELETE = lambda table_name, **kwargs: _build_delete_statement( table_name, **kwargs)

    DELETE_ALL = lambda table_name: f"DELETE * FROM {table_name}"

    def __str__( self):
        return str(self.value)

    def __call__( self, *args):
        return self.value( *args)

#####################################
#                                   #
#   Helper Functions for SQLiteDB   #
#                                   #
#####################################
def _dd_split( dd):
    cols, vals = list(), list()
    if dd:
        for k, v in dd.items():
            cols.append( k)
            vals.append( v)
    return cols, vals

def _fix_query_params( query, vals):
    query = str(query)
    if isinstance( vals, str) or isinstance( vals, int):
        vals = (vals, )
    return query, vals

##################
#                #
#   Main Class   #
#                #
##################
class SQLiteDB:
    def __init__( self, *args):
        self.file = self.DEFAULT_DB if len(args) == 0 else args[0]

    def connect( self):
        return sqlite3.connect( self.file)

    def _setter( self, query, vals=tuple()):
        query, vals = _fix_query_params( query, vals)

        conn = self.connect()
        with conn:
            conn.execute( query, tuple( map( str, vals)) )
        conn.close()

        return True

    def _getter( self, query, vals=tuple(), only_one=False):
        query, vals = _fix_query_params( query, vals)

        conn  = self.connect()
        return_item = conn.cursor().execute( query, tuple( map( str, vals))).fetchone()
        conn.close()

        if hasattr( return_item, "__iter__") and len( return_item) == 1:
            return_item = return_item[0]
        return return_item

    def _list_getter( self, query, vals=tuple()):
        query, vals = _fix_query_params( query, vals)

        conn  = self.connect()
        return_list = conn.cursor().execute( query, tuple( map( str, vals))).fetchall()
        conn.close()

        if hasattr( return_list, "__iter__") and return_list and len( return_list[0]) == 1:
            return_list = [ tup[0] for tup in return_list]
        return return_list

    def _delete( self, table_name, dd, really_delete_all=False):
        '''FOR SAFETY REASONS: This cannot be used to delete every row
        in a database unless the "really_delete_all" flag is set.
        '''
        if not dd and really_delete_all:
            self._setter( BaseSQL.DELETE_ALL( table_name), tuple())
        else:
            cols, vals = _dd_split( dd)
            self._setter( BaseSQL.DELETE( table_name, condition_columns=cols), vals)

    def _insert( self, table_name, dd):
        if not self._select( table_name, dd):
            cols, vals = _dd_split( dd)
            self._setter( BaseSQL.INSERT(table_name, condition_columns=cols), vals)

    def _select( self, table_name, dd):
        cols, vals = _dd_split( dd)
        return self._list_getter( BaseSQL.SELECT( table_name, condition_columns=cols), vals)

    def _id( self, table_name, *args, insert_new=False):
        '''This is both a getter an a setter for autoincremented values.'''
        if table_name in self.id_tables:
            cols       = self.id_tables[ table_name]
            conditions = " AND ".join( [f'{col}=?' for col in cols])
            query      =  f"SELECT id FROM {table_name} WHERE {conditions}"
            id         = self._getter( query, args)
            if not id and insert_new:
                dd = { k: v for k, v in zip( cols, args) }
                self._insert( table_name, dd)
                id = self._getter( query, args)
            return id
        else:
            raise ValueError( f"Unkown ID Table:\t{table_name}")

    @property
    def _date_str( self):
        return dt.date.today().strftime( "%Y-%m-%d")
