from pyutil import QuickTUI, box_text

def noop( *a, **kw):
    print( box_text("Hello world!", border='B'))

number_options = *((str(num), f"Select {num}.", noop) for num in (1, 2, 3)),
NumberMenu = QuickTUI( number_options)

def letter_options( *a, **kw):
    letters =  set( a[0])
    return *((letter, f"Select {letter}.", noop) for letter in letters),
LetterMenu = QuickTUI( letter_options)

def letter_options_to_number( *a, **kw):
    return *( (t[0], t[1], NumberMenu) for t in letter_options(*a, **kw)),
BothMenu = QuickTUI( letter_options_to_number)

def main_menu_prompt( *a, **kw):
    return f"The input word is {a[0]}"

if __name__ == "__main__":
    QuickTUI((
        ( "n", "Numbers"                    , NumberMenu ),
        ( "l", "Letters"                    , LetterMenu ),
        ( "b", "Letters then numbers (both)", BothMenu   )
    ), prompt=main_menu_prompt)( 'aardvark')
