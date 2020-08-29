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

PAGE_COUNT = 2


class NoSuchOCRToolException(Exception):
    """OCRがなかったときの例外クラス

    OCRがなかったときに投げられる例外クラス．

    """
    pass


class NoSuchISBNException(Exception):
    """ISBNコードがなかったときの例外クラス

    ISBNコードがなかったときに投げられる例外クラス．

    """
    pass


def get_isbn_from_pdf(input_path):
    """PDFからISBNコードを取得

    PDFを画像に変換し，いずれか二つの手法でISBNコードを取得する．
    画像からバーコードを使ってISBNコードを取得．
    または，画像から文字列を取得し，ISBNコードを取得．

    Raises:
        NoSuchOCRToolException: OCRがなかったときに発生
        NoSuchISBNException: ISBNコードがなかったときに発生

    Returns:
        str: ISBNコード
    """

    cmd = f'echo $(pdfinfo "{input_path}" | grep -E "^Pages" | sed -E "s/^Pages: +//")'
    cmd_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    total_page_count = int(cmd_result.stdout.strip())

    with tempfile.TemporaryDirectory() as temp_path:
        last_pages = convert_from_path(
            input_path,
            first_page=total_page_count - PAGE_COUNT,
            output_folder=temp_path,
            fmt='jpeg'
        )
        # extract ISBN from using barcode
        for page in last_pages:
            for decoded_page_data in decode(page):
                if re.match('978', decoded_page_data[0].decode('utf-8', 'ignore')):
                    return decoded_page_data[0].decode('utf-8', 'ignore').replace('-', '')

        ocr_tools = pyocr.get_available_tools()
        if len(ocr_tools) == 0:
            raise NoSuchOCRToolException('Cannot find OCR tool.')

        # convert image to string and extract ISBN
        ocr_tool = ocr_tools[0]
        lang = 'jpn'
        texts = []
        for page in last_pages:
            text = ocr_tool.image_to_string(
                page,
                lang=lang,
                builder=pyocr.builders.TextBuilder(tesseract_layout=3)
            )
            texts.append(text)
        for text in texts:
            if re.search(r'ISBN978-[0-4]-[0-9]{4}-[0-9]{4}-[0-9]', text):
                return re.findall(
                    r'978-[0-4]-[0-9]{4}-[0-9]{4}-[0-9]',
                    text).pop().replace(
                    '-',
                    ''
                )

    raise NoSuchISBNException(
        f'Cannot get ISBN from image. Basename: {basename(input_path)}.'
    )
