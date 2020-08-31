"""ISBNコードを取得

PDFからISBNコードを取得する．

"""


import re
import pyocr
import tempfile
import subprocess
import pyocr.builders
from os.path import basename
from pyzbar.pyzbar import decode
from pdf2image import convert_from_path


class NoSuchISBNException(Exception):
    """ISBNコードがなかったときの例外クラス

    ISBNコードがなかったときに投げられる例外クラス．

    """
    pass


def get_isbn_from_pdf(input_path: str) -> str:
    """PDFからISBNコードを取得

    PDFを画像に変換し，いずれか二つの手法でISBNコードを取得する．
    画像からバーコードを使ってISBNコードを取得．
    または，画像から文字列を取得し，ISBNコードを取得．

    Args:
        input_path (str): ファイルパス

    Raises:
        NoSuchISBNException: ISBNコードが見つからなかったときに発生

    Returns:
        str: 本から取得したISBNコードを取得する．
    """

    cmd = f'echo $(pdfinfo "{input_path}" | grep -E "^Pages" | sed -E "s/^Pages: +//")'
    cmd_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    total_pages = int(cmd_result.stdout.strip())
    if total_pages == 0:
        raise NoSuchISBNException(
            f'Cannot get ISBN from {basename(input_path)}.'
        )

    with tempfile.TemporaryDirectory() as temp_path:
        # TODO 総ページ数が2以下のとき
        last_page_images = convert_from_path(
            input_path,
            first_page=total_pages - 2,
            output_folder=temp_path,
            fmt='jpeg'
        )

        # バーコードからISBNコードを取得する
        isbn = get_isbn_from_barcode(last_page_images)
        if isbn:
            return isbn

        # 文字列からISBNコードを取得する
        isbn = get_isbn_from_text(last_page_images)
        if isbn:
            return isbn

        raise NoSuchISBNException(
            f'Cannot get ISBN from {basename(input_path)}.'
        )


def get_isbn_from_barcode(page_images) -> str:
    """バーコードからISBNコードを取得

    画像からバーコードを使って，ISBNコードを取得する

    Args:
        page_images (PIL.Image): ページの画像

    Returns:
        str: ISBNコードを返す．
            取得できないときはNoneを返す．
    """
    for page_image in page_images:
        # バーコードからコードを抽出する
        for decoded_image in decode(page_image):
            # コードの中からISBNコードにあたるものを取得する
            if re.match('978', decoded_image[0].decode('utf-8', 'ignore')):
                return decoded_image[0].decode('utf-8', 'ignore').replace('-', '')


def get_isbn_from_text(page_images) -> str:
    """文字列からISBNコードを取得

    画像からテキスト化を行い，ISBNコードを取得する

    Args:
        page_images (PIL.Image): ページの画像

    Returns:
        str: ISBNコードを返す．
            取得できないときはNoneを返す．
    """
    ocr_tools = pyocr.get_available_tools()
    if len(ocr_tools) == 0:
        # OCRがなかったときは，テキスト抽出を利用してISBNコード取得処理を行わない
        return

    # テキスト化し，ISBNコードを取得する
    ocr_tool = ocr_tools[0]
    texts = []
    for page_image in page_images:
        text = ocr_tool.image_to_string(
            page_image,
            lang='jpn',
            builder=pyocr.builders.TextBuilder(tesseract_layout=3)
        )
        texts.append(text)

    for text in texts:
        if re.search(r'ISBN978-[0-4]-[0-9]{4}-[0-9]{4}-[0-9]', text):
            # TODO 取得してきたISBNコードが複数あるとき，どうする？
            isbn_codes = re.findall(r'978-[0-4]-[0-9]{4}-[0-9]{4}-[0-9]', text)
            return isbn_codes.pop().replace(
                '-',
                ''
            )
