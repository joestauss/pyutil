import string
import msvcrt
from pyutil.active import box_text
from functools import partial

RESERVED_CHARACTERS = ("`", "+", " ", ",", ".", *map(str, range(10)))

def _assign_characters( prompts):
    unassigned, return_dict = list(), dict()
    for prompt in prompts:
        first_character = prompt[0] if prompt else None
        if first_character and first_character not in return_dict and first_character not in RESERVED_CHARACTERS:
            return_dict[ first_character] = prompt
        else:
            unassigned.append( prompt)
    still_available = [ c for c in string.ascii_letters if c not in return_dict ]
    for i, option in enumerate( unassigned):
        return_dict[ still_available[i] ] = option
    return return_dict

def _single_character_strings_only( strings):
    return all(( len(s)==1 for s in strings ))

def _parse_options( options):
    '''choice is able to accomodate several datatypes of "options", and this
    function molds them all into the same form, returning a pair of dicts.

    Returns:
        prompts     : { key_stroke_character : prompt         }
        return_vals : { key_stroke_character : value_returned }

    "Options" options...
        ...where prompt = value_returned:
            1.  An iterable of strings.
            2.  An iterable of 2-tuples ( character, prompt )
            3.  A dictionary { key_stroke_character : prompt }
        ...with general return values:
            4.  An iterable of 2-tuples ( prompt, return_value)
            5.  An iterable of 3-tuples ( character, prompt, return_value)
            6.  A dictionary { prompt : return_value }

    Cases 2/4 and 3/6 will be distinguished by checking if
        all(( len( string) for string in ... ))
    '''
    if not options:
        return dict(), dict()
    if isinstance( options, dict):
        if _single_character_strings_only( options ): # Case 3
            prompts, return_vals = options, options
        else: # Case 6
            prompts     = _assign_characters( options.keys() )
            return_vals = { key : options[ prompt] for key, prompt in prompts.items()}
    elif hasattr( options, "__iter__"):
        first_option = options[0]
        if isinstance( first_option, str): # Case 1
            prompts     = _assign_characters( options )
            return_vals = prompts
        elif isinstance( first_option, tuple):
            if len( first_option)== 3: # Case 5
                prompts     = { t[0] : t[1] for t in options}
                return_vals = { t[0] : t[2] for t in options}
            elif len( first_option)== 2:
                if _single_character_strings_only(( t[0] for t in options )): # Case 2
                    prompts     = { t[0] : t[1] for t in options}
                    return_vals = prompts
                else: # Case 4
                    return _parse_options( { t[0] : t[1] for t in options})
            else:
                raise ValueError
        else:
            raise ValueError
    else:
        raise ValueError
    return prompts, return_vals

def _choice( options, prompt=None ):
    prompts, return_vals = _parse_options( options)
    while True:
        if prompt:
            print( prompt)
        print("\n".join(( f"\t{key}\t{prompt}" for key, prompt in prompts.items())) + "\n")
        response = chr(msvcrt.getch()[0])
        if response in prompts:
            return return_vals[ response]
        print()

PREV_PAGE = "Return to the previous page."
NEXT_PAGE = "Go to the next page."
def _paginated_options( page, page_number, max_page):
    prompts, raw_return_vals = _parse_options( page)
    return_vals = { p: raw_return_vals[k] for k, p in prompts.items() }
    if page_number != 0:
        prompts[ ","] = PREV_PAGE
    if page_number != max_page:
        prompts[ "."] = NEXT_PAGE
    return prompts, return_vals

def _paginated_choice(options, prompt=None, page_size=30):
    current_page = 0
    max_page = (len( options) - 0.1) // page_size if options else 0
    options_list = list(options.items()) if isinstance(options, dict) else list( options)
    while True:
        lb = current_page * page_size
        ub = (current_page + 1) * (page_size)
        page = options_list[ lb: ub]
        prompts, return_vals = _paginated_options( page, current_page, max_page)
        response = _choice( prompts, prompt=prompt) # will return a prompt
        if response == NEXT_PAGE and current_page != max_page:
            current_page += 1
        if response == PREV_PAGE and current_page != 0:
            current_page -= 1
        if response in return_vals:
            return return_vals[ response]
        print()

choice = _paginated_choice
    #   choice is the only object imported into the module.

def _menu( *args, options, prompt=None, escape_key='`', escape_prompt='Return.', **kwargs):
    while True:
        options2, prompt2 = options, prompt
        if callable( options):
            options2 = options( *args, **kwargs)
        if callable( prompt):
            prompt2  = prompt(  *args, **kwargs)

        options2 = list( options2)
        options2.append(( escape_key, escape_prompt, escape_prompt))

        if prompt2:
            print( box_text( prompt2))

        menu_response = choice(  options2)

        if menu_response == escape_prompt:
            return
        elif isinstance( menu_response, tuple):
            action_items = menu_response
        elif callable( menu_response):
            action_items = ( menu_response, )
        else:
            raise ValueError

        for staged_action in action_items:
            return_value = staged_action( *args, **kwargs)
            kwargs = return_value if isinstance( return_value, dict) else kwargs

def QuickTUI( options, prompt=None):
    return partial( _menu, options=options, prompt=prompt)
