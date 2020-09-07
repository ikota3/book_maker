"""GUIのバリデーター

GUIの入力パラメーターのバリデーターチェックを行う

"""

import os
from app_constants import (
    FILE_TYPES,
    INPUT_ERROR,
    IS_NOT_DIR_MESSAGE,
    SELECT_DIR_MESSAGE,
    FILE_TYPE_IS_NOT_CHOSEN_MESSAGE,
    FILE_TYPE_IS_NOT_IN_THE_LIST_MESSAGE
)


class ValidateError(Exception):
    """エラーになったときの例外クラス

    エラーになったときに投げられる例外クラス．

    """
    pass


def watcher_thread_is_alive(watcher_thread) -> bool:
    """監視スレッドが生きているか

    監視スレッドが生きているかを判別する．

    Args:
        watcher_thread (threading.Thread): 監視スレッド

    Returns:
        bool: 監視スレッドが生きているときはTrue，
            死んでいるときはFalseを返す．
    """
    if watcher_thread is not None and watcher_thread.is_alive():
        return True
    return False


def _is_empty(str_: str) -> bool:
    """文字列が空か

    文字列が空であるかを判別する

    Args:
        str_ (str): 文字列

    Returns:
        bool: 文字列が空のときはTrue，
            空でないときはFalseを返す．
    """
    if str_:
        return False

    return True


def _is_dir(file_path: str) -> bool:
    """ディレクトリであるか

    ディレクトリであるかを判別する

    Args:
        file_path (str): ファイルパス

    Returns:
        bool: ディレクトリであるときはTrue，
            ディレクトリではないときはFalseを返す．
    """
    if _is_empty(file_path):
        return False

    if not os.path.isdir(file_path):
        return False

    return True


def validate_dir(file_path: str, dir_type: str) -> None:
    """入力パラメータがディレクトリであるか

    入力パラメータがディレクトリかを判別する

    Args:
        file_path (str): ファイルパス
        dir_type (str): チェックするディレクトリの種類

    Raises:
        ValidateError: ディレクトリが空のときや，ディレクトリではないときに発生する．
    """
    if _is_empty(file_path):
        raise ValidateError(INPUT_ERROR, SELECT_DIR_MESSAGE.format(dir_type))

    if not _is_dir(file_path):
        raise ValidateError(INPUT_ERROR, IS_NOT_DIR_MESSAGE.format(dir_type))


def validate_file_type(file_type: str) -> None:
    """入力パラメータが正しい拡張子か

    入力パラメータが正しい拡張子であるかを判別する

    Args:
        file_type (str): ファイルタイプ

    Raises:
        ValidateError: 入力した拡張子が空のときや，拡張子がFILE_TYPESにないときに発生する．
    """
    if _is_empty(file_type):
        raise ValidateError(
            INPUT_ERROR,
            FILE_TYPE_IS_NOT_CHOSEN_MESSAGE
        )

    if file_type not in FILE_TYPES:
        raise ValidateError(
            INPUT_ERROR,
            FILE_TYPE_IS_NOT_IN_THE_LIST_MESSAGE
        )
