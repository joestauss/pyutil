from pyutil.active import SQLiteDB
from pathlib     import Path
from collections import namedtuple

RESOURCE_FILE  = Path( __file__).parent / "box_text Resources.db"
DEFAULT_BORDER = "A"

def box_text( *args, border=DEFAULT_BORDER):
    def unpack_strings( obj):
        """Unpack parameter into a list of strings.  Recursive function."""
        if isinstance( obj, str):
            return obj.split( "\n")
        elif not hasattr(obj, '__iter__'):
            return [ str (obj)]
        else:
            lines = [ ]
            for item in obj:
                lines = lines + unpack_strings( item)
            return lines

    def get_ascii_blocks( border_type):
        db = SQLiteDB( RESOURCE_FILE )
        _, _, L, R, T, B, TL, TR, BL, BR = db._select( "Border", {"name" : border_type})[0]
        Border = namedtuple( "Border", "L R T B TL TR BL BR")
        return Border( *(db._select( "AsciiBlock", {"id" : id})[0][1] for id in (L, R, T, B, TL, TR, BL, BR)) )

    def multiline_concatenate( a, b):
        SPLIT_CHAR = '''
'''
        a_words = a.replace( "\r", "").split( SPLIT_CHAR)
        b_words = b.replace( "\r", "").split( SPLIT_CHAR)
        if len( a_words) != len( b_words):
            raise ValueError
        return SPLIT_CHAR.join( f"{a_words[i]}{b_words[i]}" for i in range( len( a_words)))

    # Unpack values.
    lines = unpack_strings( args)
    MAX_LEN = max( map( lambda s: len(s), lines))
    BUFFER  = 5
    BLANK   = " " * (MAX_LEN + 2 * BUFFER)
    TEXT    = [ BLANK ] + [ f"{' '*BUFFER}{line}{' '*(MAX_LEN-len(line))}{' '*BUFFER}" for line in lines] + [ BLANK ]
    ascii = get_ascii_blocks( border )

    # Construct top block row.
    num_T = (MAX_LEN + 2 * BUFFER)
    TOP = ascii.TL
    for _ in range( num_T):
        TOP = multiline_concatenate( TOP, ascii.T)
    TOP = multiline_concatenate( TOP, ascii.TR)

    # Construct middle block row.
    num_L = len( TEXT)
    num_R = num_L
    LEFT = "\n".join( [ascii.L] * num_L )
    RIGHT = "\n".join( [ascii.R] * num_R )
    MID = multiline_concatenate( LEFT, multiline_concatenate( "\n".join(TEXT), RIGHT))

    # Construct bottom block row.
    num_B = num_T
    BOTTOM = ascii.BL
    for _ in range( num_B):
        BOTTOM = multiline_concatenate( BOTTOM, ascii.B)
    BOTTOM = multiline_concatenate( BOTTOM, ascii.BR)

    return "\n".join(( TOP, MID, BOTTOM ))
