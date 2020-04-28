import re
import json
import requests
from box import Box


GOOGLE_API_KEY = 'xxx'
GOOGLE_API_URL = f'https://www.googleapis.com/books/v1/volumes?key={GOOGLE_API_KEY}'
GOOGLE_API_QUERY = '&q=isbn:{}'

OPENBD_API_URL = 'https://api.openbd.jp/v1/get'
OPENBD_API_QUERY = '?isbn={}'

HEADERS = {"content-type": "application/json"}


class BookInfo():
    def __init__(self, title, author):
        self.title = title
        self.author = author

    def __str__(self):
        return f'<{self.__class__.__name__}>{json.dumps(self.__dict__, indent=4, ensure_ascii=False)}'


def _format_title(title):
    # 全角括弧、全角空白を半角スペースに置換
    title = re.sub('[（）　]', ' ', title).rstrip()
    return re.sub(' +', ' ', title)


def _format_author(author):
    # OPENBD限定: 著／以降の文字列を削除する
    return re.sub('／.+', '', author)


def bookinfo_from_google(isbn):
    res = requests.get(GOOGLE_API_URL + GOOGLE_API_QUERY.format(isbn),
                       headers=HEADERS)
    if res.status_code == 200:
        google_res = Box(res.json(), camel_killer_box=True)
        if google_res is not None and google_res.total_items > 0:
            google_item = google_res['items'][0]
            title = _format_title(
                f'{google_item.volume_info.title} {google_item.volume_info.subtitle}'
            )
            author = google_item.volume_info.authors[0]
            return BookInfo(title=title, author=author)


def bookinfo_from_openbd(isbn):
    res = requests.get(OPENBD_API_URL + OPENBD_API_QUERY.format(isbn),
                       headers=HEADERS)
    if res.status_code == 200:
        openbd_res = Box(res.json()[0], camel_killer_box=True)
        if openbd_res is not None:
            open_bd_summary = openbd_res.summary
            title = _format_title(open_bd_summary.title)
            author = _format_author(open_bd_summary.author)
            return BookInfo(title=title, author=author)


if __name__ == '__main__':
    isbn = '9784297111977'
    google = bookinfo_from_google(isbn)
    print(google)
    openbd = bookinfo_from_openbd(isbn)
    print(openbd)
