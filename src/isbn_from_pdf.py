import re
import sys
import pyocr
import tempfile
import subprocess
import pyocr.builders
from os.path import basename
from pyzbar.pyzbar import decode
from pdf2image import convert_from_path


PAGE_COUNT = 2


class NoSuchOCRToolException(Exception):
    pass


class NoSuchISBNException(Exception):
    pass


def get_isbn_from_pdf(input_path):
    """
    Convert PDF to image and extract ISBN.
    Using barcode or text extraction.

    :return: ISBN
    """

    input_path = input_path
    texts = []
    cmd = f'echo $(pdfinfo "{input_path}" | grep -E "^Pages" | sed -E "s/^Pages: +//")'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    total_page_count = int(result.stdout.strip())

    with tempfile.TemporaryDirectory() as temp_path:
        last_pages = convert_from_path(input_path,
                                       first_page=total_page_count - PAGE_COUNT,
                                       output_folder=temp_path,
                                       fmt='jpeg')
        # extract ISBN from using barcode
        for page in last_pages:
            decoded_data = decode(page)
            for data in decoded_data:
                if re.match('978', data[0].decode('utf-8', 'ignore')):
                    return data[0].decode('utf-8', 'ignore').replace('-', '')

        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            raise NoSuchOCRToolException(f'Cannot find OCR tool.')
        # convert image to string and extract ISBN
        tool = tools[0]
        lang = 'jpn'
        for page in last_pages:
            text = tool.image_to_string(
                page,
                lang=lang,
                builder=pyocr.builders.TextBuilder(tesseract_layout=3)
            )
            texts.append(text)
        for text in texts:
            if re.search(r'ISBN978-[0-4]-[0-9]{4}-[0-9]{4}-[0-9]', text):
                return re.findall(r'978-[0-4]-[0-9]{4}-[0-9]{4}-[0-9]', text).pop().replace('-', '')

    raise NoSuchISBNException(f'Cannot get ISBN from image. Basename: {basename(input_path)}.')
