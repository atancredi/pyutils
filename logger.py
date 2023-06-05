#type: ignore
from logging import StreamHandler, DEBUG, Logger, getLogger, root, Formatter
import json
import math
from typing import Optional
from time import time

# (stack)logger VERSION: v1.2.0
# 1.0.0: old version
# 1.1.0: refactored
# 1.2.0: added timelog

#REGION classes
class Payload(Serializable,Settable):
    message: str = ""
    severity: str = ""
    timestamp: Optional[dict] = None
    thread: Optional[int] = None
    extra: Optional[dict] = None

class StackloggingHandler(StreamHandler):
    def __init__(self, stream=None, pretty=False, reduced_output=False):
        super(StackloggingHandler, self).__init__()
        self.pretty = pretty
        self.reduced_output=reduced_output
    def format(self, record):

        message = super(StackloggingHandler, self).format(record)
        payload = format_stackdriver_json(record, message, self.reduced_output)

        if self.pretty:
            import pprint
            return pprint.pformat(payload)
        else: return json.dumps(payload)

class StackLogger:
    def __init__(self, level=DEBUG, formatter=None, pretty=False, reduced_output=False) -> None:
        self.level = level
        self.formatter = formatter
        self.pretty = pretty
        self.reduced_output = reduced_output

        self.remove_all_loggers()
        self.logger, self.logger_handler = self.set_root_logger()

    def set_root_logger(self):
        logger = getLogger()
        logger.setLevel(self.level)

        logger_handler = StackloggingHandler(pretty=self.pretty,reduced_output=self.reduced_output)
        logger_handler.setLevel(self.level)
        if self.formatter:
            logger_handler.setFormatter(self.formatter)

        logger.propagate = True
        logger.disabled = False
        logger.addHandler(logger_handler)

        return logger, logger_handler

    def remove_all_loggers(self,include_root=True):
        loggers = self.getAll()
        if include_root:
            loggers.append(getLogger())
        for l in loggers:
            l.propagate = False
            l.disabled = True
            l.handlers.clear()

    def set_level(self,level):
        self.logger.setLevel(level)
        self.logger.removeHandler(self.logger_handler)
        self.logger_handler.setLevel(level)
        self.logger.addHandler(self.logger_handler)

    def get_all(self):
        return [getLogger(name) for name in root.manager.loggerDict]

    def get(self):
        return self.logger
#ENDREGION

#REGION timelog
class Timelog:
    time: float

    def __enter__(self):
        self.time = time()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.time = time() - self.time
#ENDREGION

#REGION methods
RESERVED = frozenset(
    (
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "id",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
    )
)

def get_extra_keys(record, reserved=RESERVED):
    extra_keys = []
    for key, value in record.__dict__.items():
        if key not in reserved and not key.startswith("_"):
            extra_keys.append(key)
    return extra_keys

def format_stackdriver_json(record, message, reduced_output):
    subsecond, second = math.modf(record.created)
    payload = Payload()
    if reduced_output:
        payload.message = message
        payload.severity = record.levelname
    else:
        payload.message = message
        payload.severity = record.levelname
        payload.thread = record.thread
        payload.timestamp = {"seconds": int(second), "nanos": int(subsecond * 1e9)}

    extra_keys = get_extra_keys(record)

    if len(extra_keys) > 0:
        payload.extra = {}
        for key in extra_keys:
            try:
                json.dumps(record.__dict__[key])  # serialization/type error check
                payload.extra[key] = record.__dict__[key]
            except TypeError:
                payload.extra[key] = str(record.__dict__[key])

    return payload.__dict__
#ENDREGION

def new_logger(level: int = DEBUG, pretty: bool = False, reduced_output: bool = True, formatter: Formatter = None) -> Logger:
    return StackLogger(level=level, pretty=pretty, reduced_output=reduced_output, formatter=formatter).get()
