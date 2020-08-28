﻿"""ディレクトリ監視ハンドラー

ディレクトリを監視する際の操作内容．

"""

import os
import shutil
import datetime
import subprocess
from watchdog.events import PatternMatchingEventHandler
from src.logic.isbn_from_pdf import get_isbn_from_pdf, NoSuchISBNException, NoSuchOCRToolException
from src.logic.bookinfo_from_isbn import book_info_from_google, book_info_from_openbd, NoSuchBookInfoException
from src.constants.log_constants import Message, LogStatus


class Handler(PatternMatchingEventHandler):
    """パターンマッチングハンドラー

    渡された引数を使い，その拡張子を持ったファイルを使って各種操作を行う．

    Attributes:
        queue (obj: `queue`): GUI側に引き渡すためのキュー
        input_path (str): 入力ディレクトリ
        output_path (str): 出力ディレクトリ
        patterns (list[str]): 拡張子パターン
    """

    def __init__(self, queue, input_path, output_path, patterns=None):
        if patterns is None:
            patterns = ['*.pdf']
        super(Handler, self).__init__(patterns=patterns,
                                      ignore_directories=True,
                                      case_sensitive=False)
        self.queue = queue
        self.input_path = input_path

        # 入力ディレクトリと出力ディレクトリが同じとき，
        # 出力ディレクトリとして現在時刻を使って新たにディレクトリを作成する
        if input_path == output_path:
            self.output_path = os.path.join(
                self.input_path,
                datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            )
        else:
            self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)

        # tmpディレクトリを出力ディレクトリ内部に作成する
        self.tmp_path = os.path.join(self.output_path, 'tmp')
        os.makedirs(self.tmp_path, exist_ok=True)

    def __del__(self):
        """後処理を行う

        出力ディレクトリの中に作成したtmpディレクトリの後始末や，
        出力ディレクトリ自体の後始末を行う．

        """
        # tmpディレクトリが空のとき，tmpディレクトリを削除する
        tmp_files_len = len(os.listdir(self.tmp_path))
        if tmp_files_len == 0:
            os.rmdir(self.tmp_path)

        # 出力ディレクトリが空のとき，出力ディレクトリを削除する
        output_files_len = len(os.listdir(self.output_path))
        if output_files_len == 0:
            os.rmdir(self.output_path)

    def _book_info_from_each_api(self, isbn, event_src_path):
        """各APIを使って本の情報を取得

        Google Books API，OPENBDを使って，本の情報を取得する．

        Args:
            isbn (str): ISBNコード
            event_src_path (str): 情報を取得する本のファイルパス
        """
        google_book_info = None
        try:
            google_book_info = book_info_from_google(isbn)
        except NoSuchBookInfoException as e:
            self.queue.put(Message(LogStatus.WARNING, e.args[0]))

        if google_book_info:
            self.queue.put(
                Message(
                    LogStatus.INFO,
                    f'<Google> title: {google_book_info.title}, author: {google_book_info.author}'
                )
            )
            self._rename_and_move_pdf(google_book_info, event_src_path)
            return

        openbd_book_info = None
        try:
            openbd_book_info = book_info_from_openbd(isbn)
        except NoSuchBookInfoException as e:
            self.queue.put(Message(LogStatus.WARNING, e.args[0]))

        if openbd_book_info:
            self.queue.put(
                Message(
                    LogStatus.INFO,
                    f'<openBD> title: {openbd_book_info.title}, author: {openbd_book_info.author}'
                )
            )
            self._rename_and_move_pdf(openbd_book_info, event_src_path)

    def _rename_and_move_pdf(self, book_info, event_src_path):
        """本の情報を使ってファイル名を変更

        本の情報を使ってファイル名を変更し，出力ディレクトリに移動させる．

        Args:
            book_info (obj: `BookInfo`): 本の情報
            event_src_path (str): リネーム対象ファイルパス
        """
        # ファイル名を本の情報を使って変更する
        pdf_rename_path = os.path.join(
            os.path.dirname(event_src_path),
            f'[{book_info.author}]{book_info.title}.pdf'
        )
        os.rename(event_src_path, pdf_rename_path)

        # 出力ディレクトリに同じファイル名のものがあるとき，tmpフォルダに移動させる
        output_path_with_basename = os.path.join(
            self.output_path,
            os.path.basename(pdf_rename_path)
        )
        if os.path.isfile(output_path_with_basename):
            shutil.move(pdf_rename_path, self.tmp_path)
            self.queue.put(
                Message(
                    LogStatus.WARNING,
                    f'PDF file already exists! Move {os.path.basename(pdf_rename_path)} to {self.tmp_path}'
                )
            )
        else:
            shutil.move(pdf_rename_path, self.output_path)
            self.queue.put(
                Message(
                    LogStatus.INFO,
                    f'Move {os.path.basename(pdf_rename_path)} to {self.output_path}'
                )
            )

    def on_created(self, event):
        """作成イベント感知メソッド

        `__init__`で定義したパターンに従ったファイルが作成されたイベントを感知し，
        ISBNコードを使ってファイル名を正しい本の題名に変更させる．

        Args:
            event (obj: `watchdog.events.DirCreatedEvent` or `watchdog.events.FileCreatedEvent`): イベント情報
        """
        shell_path = os.path.join(
            os.path.dirname(__file__),
            '../../getISBN.sh'
        )
        event_src_path = event.src_path
        cmd = f'{shell_path} {event_src_path}'
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        try:
            if result.returncode == 0:
                # ISBNコードをシェルから取得
                isbn = result.stdout.strip()
                self.queue.put(
                    Message(
                        LogStatus.INFO,
                        f'ISBN from Shell -> {isbn}'
                    )
                )
                self._book_info_from_each_api(isbn, event_src_path)

            else:
                # ISBNコードをバーコードから，または文字列から取得
                isbn = get_isbn_from_pdf(event_src_path)
                self.queue.put(
                    Message(
                        LogStatus.INFO,
                        f'ISBN from Python -> {isbn}'
                    )
                )
                self._book_info_from_each_api(isbn, event_src_path)

        except (NoSuchISBNException, NoSuchOCRToolException) as e:
            # ISBNコードが見つからなかったとき
            if isinstance(e, NoSuchISBNException):
                self.queue.put(Message(LogStatus.WARNING, e.args[0]))

            # OCRツールが見つからなかったとき
            if isinstance(e, NoSuchOCRToolException):
                self.queue.put(Message(LogStatus.ERROR, e.args[0]))
                raise

            shutil.move(event_src_path, self.tmp_path)
            self.queue.put(
                Message(
                    LogStatus.WARNING,
                    f'Move {os.path.basename(event_src_path)} to {self.tmp_path}'))
