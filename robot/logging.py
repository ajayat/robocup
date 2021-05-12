import sys
import utime


_START_TIME = utime.time()
LEVELS = {"DEBUG":0, "INFO":1, "WARNING":2, "ERROR":3, "CRITICAL":4}


class Handler:
    """
    A class that gives general methods of a handler and attributes access control.
    """

    def __init__(self):
        super().__init__()
        self._level = 1  # default to INFO
        self._formatter = "{level} -> {message}" # default format

    @property
    def level(self) -> int:
        return self._level

    def set_level(self, level):
        """
        level: Can be DEBUG, INFO, WARNING, ERROR or CRITICAL, or a int from 0 to 4
        """
        if isinstance(level, str):
            # if level is a string, get its associated number
            level = LEVELS.get(level)
        self._level = level


class FileHandler(Handler):

    def __init__(self, file: str):
        super().__init__()
        self.__file = file
        self._level = 0  # default to DEBUG
        self.formatter = "{level}: {name} (+{time}s) -> {message}"

    def write(self, content: str):
        """
        A context manager to write data into the file, and close after
        """
        with open(self.__file, "a", encoding="utf-8") as logfile:
            logfile.write(content+"\n")
            logfile.flush()


class StreamHandler(Handler):

    def __init__(self):
        self._level = 1  # default to INFO
        self.formatter = "{level}: {name} -> {message}"

    def write(self, content: str):
        """
        Writes data to the output console
        """
        sys.stdout.write(content+"\n")


class Logger:
    """
    A class to perform filtering log message before sending to handlers
    """
    # A dict containing all instances of logger, we can get a logger with its name
    LOGGERS = {}

    def __new__(cls, name: str):
        """
        The real constructor, return an instance with a given name or create one.
        """
        if not name in cls.LOGGERS:
            cls.LOGGERS[name] = super().__new__(cls)
        return cls.LOGGERS[name]

    def __init__(self, name: str):
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
    def handlers(self):
        """
        Get all handlers that are accessible by the logger
        (i.e, if propagate was set to True, data were sent to root's handlers)
        """
        if self.name != 'root' and self.propagate and 'root' in self.LOGGERS:
            return self._handlers + self.LOGGERS['root'].handlers
        return self._handlers

    def set_level(self, level):
        """
        level: Can be DEBUG, INFO, WARNING, ERROR or CRITICAL, or a int from 0 to 4
        """
        if isinstance(level, str):
            level = LEVELS.get(level)
        self._level = level

    def add_handler(self, handler: Handler):
        """
        handler: a Handler class (FileHandler or StreamHandler)
        """
        self._handlers.append(handler)

    def __repr__(self) -> str:
        return "Logger(name={}, level={})".format(self.name, self._level)
