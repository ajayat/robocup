# This module is similar to the logging CPython3 module
# https://docs.python.org/3/howto/logging.html

import sys
import utime

_START_TIME = utime.time()
LEVELS = {"DEBUG":0, "INFO":1, "WARNING":2, "ERROR":3, "CRITICAL":4}


class Handler:
    """
    A class that gives general methods of a handler used for I/O operations.

    Methods:
        set_level(level: int | str): sets the log level for filtering logs.
    """

    def __init__(self):
        self._level = 1  # default to INFO
        self._formatter = "{level} -> {message}" # default format

    @property
    def level(self) -> int:
        return self._level

    def set_level(self, level):
        """
        Sets the log level for filtering logs at the handler scope.
        Parameters:
            level: Can be DEBUG, INFO, WARNING, ERROR or CRITICAL, or a int from 0 to 4
        """
        if isinstance(level, str):
            # if level is a string, get its associated number
            level = LEVELS.get(level)
        self._level = level


class FileHandler(Handler):
    """ 
    A handler used to performs files operations.
    
    Attributes:
        file: the file path
        formatter: Sets a format for logs 
            default format is "{level}: {name} (+{time}s) -> {message}"
    Methods:
        write(content: str): write a line in the specified file
    """
    def __init__(self, file: str):
        super().__init__()
        self.file = file
        self._level = 0  # default to DEBUG
        self.formatter = "{level}: {name} (+{time}s) -> {message}"

    def write(self, content: str):
        """
        Uses a context manager to write data into the specified file, and close after.
        Parameters:
            content (str): a log line to write in a file
        """
        with open(self.__file, "a", encoding="utf-8") as logfile:
            logfile.write(content+"\n")
            logfile.flush()


class StreamHandler(Handler):
    """ 
    A handler used to write logs in the output console
    
    Attributes:
        formatter: Sets a format for logs 
            default format is "{level}: {name} (+{time}s) -> {message}"
    Methods:
        write(content: str): writes a line in the sys.stdout stream
    """
    def __init__(self):
        self._level = 1  # default to INFO
        self.formatter = "{level}: {name} -> {message}"

    def write(self, content: str):
        """ Writes a formatted line to the output console (sys.stdout) """
        sys.stdout.write(content+"\n")


class Logger:
    """
    A class to perform filtering log messages before sending to handlers.

    Attributes:
        name: the logger's name
        propagate: if set to True (default), logs will be written in root's handlers.
        handlers: returns all handlers that the logger can see.
    Methods:
        log(level, message): send a line to handlers with a given level
        set_level(level)
        add_handler(handler)

    Conventionnal usage:
    logger = logging.Logger(__name__)
    """
    # A dict containing all instances of logger, we can get a logger with its name
    LOGGERS = {}

    def __new__(cls, name: str):
        """
        The real constructor, used to check if an instance with the same name already exists:
        Parameters:
            name: The return an instance with a given name or create one.
        """
        if not name in cls.LOGGERS:
            cls.LOGGERS[name] = super().__new__(cls)
        return cls.LOGGERS[name]

    def __init__(self, name: str):
        """ Initialize the logger
        Parameters:
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

    def log(self, level, message: str):
        """
        Tests if the log's request level is superior to the logger level,
        then format the string with the format of the handler and write it.
        Parameters:
            level (str | int): 
                can be DEBUG, INFO, WARNING, ERROR or CRITICAL, or a int from 0 to 4
            message (str)
        
        Shortcuts methods are debug(), info(), error(), warning() and critical().
        """
        if self._level <= LEVELS[level]:
            for handler in self.handlers:
                content = handler.formatter.format(
                    level=level,
                    name=self.name,
                    time=utime.time()-_START_TIME,
                    message=message
                )
                if handler.level <= LEVELS[level]:
                    handler.write(content)

    @property
    def handlers(self) -> list:
        """
        Returns a list of handlers that are accessible by the logger.
        (i.e, if propagate was set to True, data were sent to root's handlers)
        """
        if self.name != 'root' and self.propagate and 'root' in self.LOGGERS:
            return self._handlers + self.LOGGERS['root'].handlers
        return self._handlers

    def set_level(self, level):
        """
        Sets the logger's level.
        Parameters:
            level: Can be DEBUG, INFO, WARNING, ERROR or CRITICAL, or a int from 0 to 4
        """
        if isinstance(level, str):
            level = LEVELS.get(level)
        self._level = level

    def add_handler(self, handler: Handler):
        """
        Add an Handler instance to the logger.
        Parameters:
            handler: a Handler class (FileHandler or StreamHandler)
        """
        self._handlers.append(handler)

    def __repr__(self) -> str:
        return "Logger(name={}, level={})".format(self.name, self._level)
