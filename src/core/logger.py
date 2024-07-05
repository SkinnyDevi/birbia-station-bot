from datetime import datetime
from enum import Enum


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    GRAY = "\033[90m"


class BirbiaLogger:
    """
    Birbia's own custom logger.
    """

    class LogLevel(Enum):
        """Enum for log levels."""

        INFO = 1
        WARN = 2
        ERROR = 3
        DEBUG = 4

    LOG_LEVEL = LogLevel.DEBUG

    __PREFIX = bcolors.ENDC + bcolors.OKCYAN + " [BIRBIA] "
    __INFO = bcolors.OKBLUE + "INFO" + __PREFIX
    __WARN = bcolors.WARNING + "WARN" + __PREFIX
    __ERROR = bcolors.FAIL + "ERROR" + __PREFIX
    __DEBUG = bcolors.OKGREEN + "DEBUG" + __PREFIX

    __log: list[str] = []

    @staticmethod
    def info(msg: str):
        """
        General logging of actions.
        """

        if BirbiaLogger.LOG_LEVEL != BirbiaLogger.LogLevel.DEBUG:
            if BirbiaLogger.LOG_LEVEL.value > BirbiaLogger.LogLevel.INFO.value:
                return

        msg = bcolors.ENDC + msg
        log = f"{BirbiaLogger.__now()} {BirbiaLogger.__INFO}{msg}"
        BirbiaLogger.__log.append(log)
        print(log)

    @staticmethod
    def warn(msg: str, *args):
        """
        Logging for any warning presented.
        """

        if BirbiaLogger.LOG_LEVEL != BirbiaLogger.LogLevel.DEBUG:
            if BirbiaLogger.LOG_LEVEL.value > BirbiaLogger.LogLevel.WARN.value:
                return

        if args != ():
            msg += f" {str(*args)}"

        msg = bcolors.ENDC + msg
        log = f"{BirbiaLogger.__now()} {BirbiaLogger.__WARN}{msg}"
        BirbiaLogger.__log.append(log)
        print(log)

    @staticmethod
    def error(msg: str, *args):
        """
        Used to called on try/except statements.
        """

        if BirbiaLogger.LOG_LEVEL != BirbiaLogger.LogLevel.DEBUG:
            if BirbiaLogger.LOG_LEVEL.value > BirbiaLogger.LogLevel.ERROR.value:
                return

        if args != ():
            msg += f" {str(*args)}"

        msg = bcolors.ENDC + bcolors.FAIL + msg
        log = f"{BirbiaLogger.__now()} {BirbiaLogger.__ERROR}{msg}"
        BirbiaLogger.__log.append(log)
        print(log)

    @staticmethod
    def debug(msg: str):
        """
        General debug. Not recorded in the internal log history.
        """
        if BirbiaLogger.LOG_LEVEL != BirbiaLogger.LogLevel.DEBUG:
            return

        msg = bcolors.ENDC + msg
        print(f"{BirbiaLogger.__now()} {BirbiaLogger.__DEBUG}{msg}")

    @staticmethod
    def __now():
        return f"{bcolors.BOLD}{bcolors.GRAY}{str(datetime.now())[:-7]}"
