import os
from src.gui.app_constants import (FILE_TYPES, INPUT_ERROR, IS_NOT_DIR_MESSAGE, SELECT_DIR_MESSAGE,
                                   FILE_TYPE_IS_NOT_CHOSEN_MESSAGE, FILE_TYPE_IS_NOT_IN_THE_LIST_MESSAGE)


class ValidateError(Exception):
    pass


def _is_empty(str_: str) -> bool:
    """
    If the argument is not empty, return False.
    Otherwise True.
    :param str_: string.
    :return: boolean.
    """
    if str_:
        return False

    return True


def _is_dir(dir_path: str) -> bool:
    """
    If the argument is not dir, return False.
    Otherwise True.
    :param dir_path: string. directory path.
    :return: boolean.
    """
    if _is_empty(dir_path):
        return False

    if not os.path.isdir(dir_path):
        return False

    return True


def validate_dir(dir_path: str, dir_type: str) -> None:
    """
    Validate dir_path.
    :param dir_path: string. directory path.
    :param dir_type: string. directory type.
    :raise ValidateError: raise error, when validation fails.
    :return: None.
    """
    if _is_empty(dir_path):
        raise ValidateError(INPUT_ERROR, SELECT_DIR_MESSAGE.format(dir_type))

    if not _is_dir(dir_path):
        raise ValidateError(INPUT_ERROR, IS_NOT_DIR_MESSAGE.format(dir_type))


def validate_file_type(file_type: str) -> None:
    """
    Validate file_type.
    :param file_type: string. file type.
    :raise ValidateError: raise error, when validation fails.
    :return: None.
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
