from pyutil import box_text

borders = ( 'A', 'B', 'C')

for border in borders:
    lines = [ 'Hello\nworld', '!', 'helloworldhelloworldhelloworld']
    print( box_text( lines, border=border) + "\n\n" )
