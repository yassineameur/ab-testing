"""
Export a single function that returns a logger configured
"""
import datetime
import logging
import sys
from os import environ

import structlog
from structlog import get_logger


def _configure_root_logger():
    """
    This function configures the root logger:
        - We set the logging level.
        - We add a stream handler to display the messages coming from structlogger as they are.
    """

    root_logger = logging.getLogger()
    logging_level = environ.get("LOGGER_LEVEL", "INFO").upper()
    root_logger.setLevel(logging_level)

    handler = logging.StreamHandler(sys.stdout)
    # the formatter makes sure that the structlog message is kept
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


# pylint: disable=unused-argument
def _replace_event_key_by_message(logger, method_name, event_dict):
    """
    This function has to hold this signature in order to respect structlog processors signature.
    It is used in structlog's processors pipeline.
    The same thing applies for the two following ones
    :param: the logger: The current struct logger.
    :param: method_name: The method name (warn, info, ...)
    :param event_dict: The dict that represents the contain of a structlog message.
    :return: the updated event dict : the 'event' key will be replaced by the key 'msg'
    """
    event_dict["msg"] = event_dict["event"]
    del event_dict["event"]
    return event_dict


def _add_log_level(_, method_name, event_dict):
    """
    This function adds the key 'level' which
     the value is the log level of the method to the events dict.
    """
    event_dict["level"] = logging.getLevelName(method_name.upper())
    return event_dict


# pylint: disable=invalid-name
def _add_time(_, __, event_dict):
    """
    This function adds the key 'time' which
     the value is the log time, to the events dict.
     For microseconds, we take only the three first digits to match chpr format.
    """
    event_dict["time"] = datetime.datetime.utcnow().isoformat()[:-3] + "Z"
    return event_dict


def _get_structlog_logger():
    """
    This function is responsible for configuring the root logger and the struct logger.
    :return: the configured structlogger
    """
    # we start by configuring the root logger to add sentry handler and format the message to keep
    # the structlogger message as it is.
    _configure_root_logger()

    # we configure the structlogger with those processors that will be
    # executed to process the message in order to produce the needed format.

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            _add_log_level,
            _add_time,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            _replace_event_key_by_message,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logger = get_logger()
    return logger


_SINGLETON_LOGGER_INSTANCE = None


# pylint: disable=invalid-name
def getLogger():
    """
    this is the main function that is used to provide the logger.
    It implements the singleton design pattern: We instantiate the logger just once.
    """

    # pylint: disable=global-statement
    global _SINGLETON_LOGGER_INSTANCE
    if _SINGLETON_LOGGER_INSTANCE is None:
        _SINGLETON_LOGGER_INSTANCE = _get_structlog_logger()
    return _SINGLETON_LOGGER_INSTANCE
