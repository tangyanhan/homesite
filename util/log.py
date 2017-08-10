# coding=utf-8
import sys
import logging


def create_logger(thread_id=-1):
    """
    Create a logger for the specified thread.
    :param thread_id: custom id for the thread. -1 for main thread.
    :return: a configured logger ready for use.
    """
    formatter = "%(asctime)s %(filename)s:%(lineno)d:%(levelname)s:%(message)s"
    if thread_id != -1:
        formatter = "Thread #{0}#".format(thread_id) + formatter

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(formatter, "%X"))
    log_level = logging.INFO
    console_handler.setLevel(log_level)

    logger_id = "log" + str(thread_id)
    logger = logging.getLogger(logger_id)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    return logger


thread_loggers = {}
def get_logger(thread_id=-1):
    # Config logger only at the first time.
    if not thread_loggers:
        reload(sys)
        sys.setdefaultencoding('utf8')

    if thread_id not in thread_loggers:
        logger = create_logger(thread_id)
        thread_loggers[thread_id] = logger
    return thread_loggers[thread_id]


log = get_logger()

