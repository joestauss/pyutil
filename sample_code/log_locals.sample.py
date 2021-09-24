from pyutil.standard_import import *

def sample_function( mandatory_arg, *optional_args, mandatory_kwarg, **optional_kwargs):
    local_variable = "Stawberry"
    log_local_variables( dev_logger)
    
sample_function( "Apple", "Banana" , "Cherry", mandatory_kwarg="Grapes")

'''
The following lines are added to Development.log:

[Current Data & Time] DEBUG	sample_function
    mandatory_arg='Apple'
    mandatory_kwarg='Grapes'
    optional_args=('Banana', 'Cherry')
    optional_kwargs={}
    local_variable='Stawberry'
'''
