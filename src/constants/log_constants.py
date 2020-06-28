from collections import namedtuple
from enum import IntEnum, auto

Message = namedtuple('Message', [
    'status',
    'message'
])


class LogStatus(IntEnum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    COMPLETED = auto()
