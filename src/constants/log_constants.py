from collections import namedtuple
from enum import Enum

Message = namedtuple('Message', [
    'status',
    'message'
])


class LogStatus(Enum):
    """
    Enums for log status
    The hex value is for colorizing the log

    Fields:
        INFO,
        WARNING,
        ERROR,
        COMPLETED
    """
    INFO = '#43a047'
    WARNING = '#fdd835'
    ERROR = '#e53935'
    COMPLETED = '#3949ab'
