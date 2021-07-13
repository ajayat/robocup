# This module is similar to the logging CPython3 module
# https://docs.python.org/3/howto/logging.html

import sys
import utime as time

_START_TIME = time.time()
LEVELS = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}


class Handler:
    """A class that gives general methods of a handler used for I/O operations."""

    def __init__(self):
        self._level = 1  # default to INFO
        self._formatter = "{level} -> {message}"  # default format

    @property
    def level(self) -> int:
        return self._level

    def set_level(self, level) -> None:
        """Sets the log level for filtering logs at the handler scope.

        Args:
            level: Can be DEBUG, INFO, WARNING, ERROR or CRITICAL, or a int from 0 to 4
        """
        if isinstance(level, str):
            # if level is a string, get its associated number
            level = LEVELS.get(level)
        self._level = level


class FileHandler(Handler):
    """A handler used to performs files operations.

    Attributes:
        file: the file path
        formatter: Sets a format for logs
            default format is "{level}: {name} (+{time}s) -> {message}"
    """

    def __init__(self, file: str):
        super().__init__()
        self.file = file
        self._level = 1  # default to INFO
        self.formatter = "{level}: {name} (+{time}s) -> {message}"

    def write(self, content: str):
        """Write data into the specified file, and close after.

        Args:
            content: a log line to write in a file
        """
        with open(self.file, "a", encoding="utf-8") as logfile:
            logfile.write(content + "\n")
            logfile.flush()


class StreamHandler(Handler):
    """A handler used to write logs in the output console

    Attributes:
        formatter: Sets a format for logs
            default format is "{level}: {name} -> {message}"
    """

    def __init__(self):
        super().__init__()
        self._level = 0  # default to DEBUG
        self.formatter = "{level}: {name} -> {message}"

    @staticmethod
    def write(content: str):
        """Writes a formatted line to the output console (sys.stdout)"""
        sys.stdout.write(content + "\n")


class Logger:
    """A class to perform filtering log messages before sending to handlers.

    Conventionnal usage:
    logger = logging.Logger(__name__)

    Attributes:
        name: The logger's name
        propagate: If set to True (default), logs will be written in root's handlers.
    """

    # A dict containing all instances of logger, we can get a logger with its name
    LOGGERS = {}

    def __new__(cls, name: str):
        """The real constructor,

        It's used to check if an instance with the same name already exists

        Args:
            name: The return an instance with a given name or create one.
        """
        if name not in cls.LOGGERS:
            cls.LOGGERS[name] = super().__new__(cls)
        return cls.LOGGERS[name]

    def __init__(self, name: str):
        """Initialize the logger.

        Args:
            name (str): the logger's name
        """
        self.name = name
        self._level = 1  # default to INFO
        self._handlers = []
        self.propagate = True

    def __getattr__(self, name: str):
        """
        Used to perform logging with a given level:
        logger.info(...) will call __getattr__(self, "info")
        """
        if name.upper() in LEVELS:
            return lambda message: self.log(name.upper(), message)

    def log(self, level: str, message: str) -> None:
        """Write a log line in a file.

        Tests if the log's request level is superior to the logger level,
        then format the string with the format of the handler and write it.
        Shortcuts methods are debug(), info(), error(), warning() and critical().

        Args:
            level: Can be DEBUG, INFO, WARNING, ERROR or CRITICAL, or a int from 0 to 4.
            message: The message to write.
        """
        if self._level <= LEVELS[level]:
            for handler in self.handlers:
                content = handler.formatter.format(
                    level=level,
                    name=self.name,
                    time=time.time() - _START_TIME,
                    message=message,
                )
                if handler.level <= LEVELS[level]:
                    handler.write(content)

    @property
    def handlers(self) -> list:
        """Returns a list of handlers that are accessible by the logger.

        If propagate was set to True, data were sent to root's handlers.

        Returns:
            A list of all handlers.
        """
        if self.name != "root" and self.propagate and "root" in self.LOGGERS:
            return self._handlers + self.LOGGERS["root"].handlers
        return self._handlers

    def set_level(self, level) -> None:
        """Sets the logger's level.

        Args:
            level: Can be DEBUG, INFO, WARNING, ERROR or CRITICAL, or a int from 0 to 4
        """
        if isinstance(level, str):
            level = LEVELS.get(level)
        self._level = level

    def add_handler(self, handler: Handler) -> None:
        """Add an Handler instance to the logger.

        Args:
            handler: A Handler class (FileHandler or StreamHandler)
        """
        self._handlers.append(handler)

    def __repr__(self) -> str:
        return "Logger(name={}, level={})".format(self.name, self._level)
