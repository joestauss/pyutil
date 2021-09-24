__all__ = [ 'dev_logger', 'feed_logger', 'log_local_variables' ]

import logging
import logging.handlers
import pathlib

############################################
#                                          #
#   Functions                              #
#    * simple_logger is a helper function. #
#    * log_local_variables gets exported.  #
#                                          #
############################################
def simple_logger( logger_name, handler, formatter, level=logging.DEBUG):
    logger = logging.getLogger( logger_name)
    handler.setFormatter( formatter)
    logger.addHandler( handler)
    logger.setLevel( level)
    return logger


def log_local_variables(logger, parent=0):
    import inspect
    DEPTH = 1  + parent
    frame = inspect.stack()[DEPTH]
    lines = [ frame.function ]
    lines += [ f"   {key}={repr(value)}" for key, value in frame[0].f_locals.items() ]
    logger.debug( "\n".join( lines ))

#####################
#                   #
#   File Locations  #
#                   #
#####################
LOG_DIRECTORY = pathlib.Path( __file__).parent
DEV_LOG       = LOG_DIRECTORY / "Development.log"
FEED_LOG      = LOG_DIRECTORY / "Feed.log"

##################
#                #
#   Formatters   #
#                #
##################
bracket_formatter = logging.Formatter( fmt='[%(asctime)s.%(msecs)03d] %(levelname)s\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
clean_formatter   = logging.Formatter( fmt="%(asctime)s : %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

################
#              #
#   Handlers   #
#              #
################
dev_handler  = logging.handlers.TimedRotatingFileHandler( DEV_LOG , when="h" , backupCount=3 )
feed_handler = logging.handlers.TimedRotatingFileHandler( FEED_LOG, when="W2", backupCount=3 )

###############
#             #
#   Loggers   #
#             #
###############
dev_logger = simple_logger(
    "Development / Debugging",
    dev_handler,
    bracket_formatter )

feed_logger = simple_logger(
    "Feed Monitor",
    feed_handler,
    clean_formatter )
