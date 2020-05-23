import logging

from django.conf import settings

logger = logging.getLogger('all_apps.custom')

MINIMUM_LOG_LEVEL=3

def log_warning(module, function, message):
    log_string = module+": "+function+": "+str(message)
    logger.warning(log_string)

def log_info(module, function, message):
    log_string = module+": "+function+": "+str(message)
    logger.info(log_string)

def log_error(module, function, message):
    log_string = module+": "+function+": "+str(message)
    logger.error(log_string)

def log_exception(e):
    logger.exception(e)

def log_level_info(level, module, function, message):
    if level >= MINIMUM_LOG_LEVEL:
        log_string = module+": "+function+": "+message
        logger.info(log_string)

def log_debug_info(module, function, message):
    if settings.DEBUG:
        log_info(module, function, message)
