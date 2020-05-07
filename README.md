# BOOK_MAKER

### Workflow
1. 監視対象のディレクトリを指定し、src/watch.py を起動
2. PDFを監視対象のディレクトリに配置
3. イベントを感知し、ファイルの中身からISBNを取得
    - ISBN取得手順
        - シェルを使い, バーコードから取得.
        - Pythonコード上で, バーコードから取得.
        - Pythonコード上で, テキストから取得.
4. 各APIから、ISBNを元に書籍情報を取得
    - 使用しているAPI
        - [Google Books APIs](https://developers.google.com/books?hl=ja)
        - [openBD](https://openbd.jp/)
5. ファイル名を修正し、ファイルを適切なディレクトリに移動

### Requirements

- Install Poppler(for PDF command)
    ```
    $ brew install poppler
    ```

- Install Tesseract(for OCR)
    ```
    $ brew install tesseract
    $ brew install tesseract-lang
    ```

- Library
    - [watchdog](https://github.com/gorakhargosh/watchdog)
    - [pdf2image](https://github.com/Belval/pdf2image)
    - [pyocr](https://gitlab.gnome.org/World/OpenPaperwork/pyocr)
    - [pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar)
    - [pillow](https://github.com/python-pillow/Pillow)
    - [requests](https://github.com/psf/requests)
    - [python-box](https://github.com/cdgriffith/Box)

- Install Library
    ```
    $ pip3 install -r requirements.txt
    ```

### How to use
```
$ python3 src/watch.py input_path [output_path] [*extensions]
```

### ちょっとした説明
(自炊するにあたってﾁｮｯﾄ自動化しようとした話)[https://qiita.com/ikota3/items/2eda80dc6906a8613a31]
