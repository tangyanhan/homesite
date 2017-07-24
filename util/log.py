import sys
import logging


def get_log():
    formatter = "%(asctime)s %(filename)s:%(lineno)d:%(levelname)s:%(message)s"

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(formatter))
    log_level = logging.INFO
    console_handler.setLevel(log_level)

    log = logging.getLogger("homesite_log")
    log.setLevel(logging.DEBUG)
    log.addHandler(console_handler)

    return log


log = get_log()
