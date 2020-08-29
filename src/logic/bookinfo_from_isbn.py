"""本の情報を取得

ISBNコードを用いて本の情報を取得する．

"""


import re
import json
import requests
from box import Box


GOOGLE_API_URL = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}'
OPENBD_API_URL = 'https://api.openbd.jp/v1/get?isbn={}'

HEADERS = {"content-type": "application/json"}


class NoSuchBookInfoException(Exception):
    """本の情報がないときの例外クラス

    本の情報が見つからなかったときに投げられる例外クラス．

    """
    pass


class BookInfo:
    """本の情報クラス

    本の情報を格納するクラス．

    Attributes:
        title (str): タイトル
        author (str): 著者
    """

    def __init__(self, title, author):
        self.title = title
        self.author = author

    def __str__(self):
        return f'<{self.__class__.__name__}>{json.dumps(self.__dict__, indent=4, ensure_ascii=False)}'


def _format_title(title):
    """タイトルを整形

    システム上保存できない文字列を置換や，全角空白を半角文字に変換を行う．

    Args:
        title (str): タイトル

    Returns:
        str: 整形後のタイトル
    """
    # 全角括弧、全角空白を半角スペースに置換
    title = re.sub('[（）　]', ' ', title).rstrip()
    return re.sub(' +', ' ', title)


def _format_author(author):
    """著者を整形

    著者に関係のない文字列を削除する．

    Note:
        OPENBDからのみ，この関数は呼び出される

    Args:
        author (str): 著者

    Returns:
        str: 整形後の著者
    """
    # 著／以降の文字列を削除する
    return re.sub('／.+', '', author)


def book_info_from_google(isbn):
    """Google Books API を使って本の情報を取得

    ISBNコードを使って，Google Books APIから本の情報を取得する．

    Args:
        isbn (bool): ISBNコード

    Raises:
        NoSuchBookInfoException: 本の情報がなかったときに発生

    Returns:
        :obj:`BookInfo`: 本の情報
    """
    res = requests.get(GOOGLE_API_URL.format(isbn), headers=HEADERS)
    if res.status_code == 200:
        google_res = Box(
            res.json(),
            camel_killer_box=True,
            default_box=True,
            default_box_attr=''
        )
        if google_res is not None and google_res.total_items > 0:
            google_item = google_res['items'][0]
            title = _format_title(
                f'{google_item.volume_info.title} {google_item.volume_info.subtitle}'
            )
            author = google_item.volume_info.authors[0]
            return BookInfo(title=title, author=author)
    else:
        raise NoSuchBookInfoException(
            f'Cannot find book info from Google.\n'
            f'ISBN: {isbn}. Status Code: {res.status_code}.'
        )


def book_info_from_openbd(isbn):
    """OPENBD を使って本の情報を取得

    Args:
        isbn (str): ISBNコード

    Raises:
        NoSuchBookInfoException: 本の情報がなかったときに発生

    Returns:
        :obj:`BookInfo`: 本の情報
    """
    res = requests.get(OPENBD_API_URL.format(isbn), headers=HEADERS)
    if res.status_code == 200:
        openbd_res = Box(
            res.json()[0],
            camel_killer_box=True,
            default_box=True,
            default_box_attr=''
        )
        if openbd_res is not None:
            open_bd_summary = openbd_res.summary
            title = _format_title(open_bd_summary.title)
            author = _format_author(open_bd_summary.author)
            return BookInfo(title=title, author=author)
    else:
        raise NoSuchBookInfoException(
            f'Cannot find book info from OPENBD.\n'
            f'ISBN: {isbn}. Status Code: {res.status_code}.'
        )
