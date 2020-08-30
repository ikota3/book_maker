"""ログ生成に関する定数など

ログメッセージ生成のための定数や，色の設定を行う．

"""


from collections import namedtuple
from enum import Enum

"""ログメッセージ

ログメッセージを格納する

Attributes:
    status (:obj: `LogStatus`): ログのステータス 
    message (str): ログのメッセージ
"""
Message = namedtuple('Message', [
    'status',
    'message'
])


class LogStatus(Enum):
    """ログメッセージの色

    ログメッセージの色を種類別に分ける

    Attributes:
        INFO,
        WARNING,
        ERROR,
        COMPLETED
    """
    INFO = '#43a047'
    WARNING = '#fdd835'
    ERROR = '#e53935'
    COMPLETED = '#3949ab'
