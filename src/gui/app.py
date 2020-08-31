from functools import partial
from queue import Queue
from datetime import datetime
from tkinter import (
    N,
    S,
    E,
    W,
    EW,
    NSEW,
    VERTICAL,
    Tk,
    Frame,
    Button,
    Entry,
    Text,
    Label,
    Scrollbar,
    StringVar,
    filedialog,
    messagebox
)
from tkinter.ttk import Combobox
from src.handler.watch import Watcher
from src.gui.app_constants import FILE_TYPES
from src.gui.app_service import watcher_thread_is_alive, validate_dir, validate_file_type, ValidateError
from src.constants.log_constants import LogStatus

ROOT = Tk()


class BookMakerApp(Frame):
    """BookMakerApp

    BookMakerAppのGUIを構築する

    Attributes:
        watch_dir_path (:obj: `StringVar`): 監視対象パス
        output_dir_path (:obj: `StringVar`): 出力対象パス
        file_type (:obj: `StringVar`): 拡張子の種類
        log_box (:obj: `Text`): ログのテキストウィジェット
        queue (:obj: `queue`): ログに出力する内容が格納されるキュー
        watcher_thread (:obj: `threading.Thread`): 監視スレッド
    """

    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.master.geometry('+1000+100')
        self.master.resizable(0, 0)
        self.master.title('Book Maker')
        self.master.protocol('WM_DELETE_WINDOW', self._exit_app)

        self.watch_dir_path = StringVar()
        self.output_dir_path = StringVar()
        self.file_type = StringVar()
        self.log_box = None
        self.queue = Queue()
        self.watcher_thread = None

        self._create_widgets()

    def _create_widgets(self):
        """ウィジェットを作成

        ウィジェットを全て作成する

        """

        # Main Frame
        main_frame = Frame(self)
        main_frame.grid(row=0, column=0, sticky=NSEW, padx=10, pady=10)

        # Function for asking directory
        def _ask_folder(dir_path):
            path = filedialog.askdirectory()
            dir_path.set(path)

        # Dir to watch
        dir_to_watch_label = Label(main_frame, text='監視ディレクトリ')
        dir_to_watch_entry = Entry(
            main_frame,
            relief='solid',
            borderwidth=1,
            textvariable=self.watch_dir_path,
        )
        dir_to_watch_button = Button(
            main_frame,
            text='参照',
            relief='solid',
            borderwidth=1,
            command=partial(_ask_folder, self.watch_dir_path)
        )

        # Output dir
        output_dir_label = Label(main_frame, text='出力ディレクトリ')
        output_dir_entry = Entry(
            main_frame,
            relief='solid',
            borderwidth=1,
            textvariable=self.output_dir_path
        )
        output_dir_button = Button(
            main_frame,
            text='参照',
            relief='solid',
            borderwidth=1,
            command=partial(_ask_folder, self.output_dir_path)
        )

        # File type
        file_type_label = Label(main_frame, text='ファイルの種類')
        file_type_combobox = Combobox(
            main_frame,
            state='readonly',
            values=FILE_TYPES,
            textvariable=self.file_type
        )
        file_type_combobox.current(0)

        # Execute
        execute_button = Button(
            main_frame,
            text='実行',
            relief='solid',
            borderwidth=1,
            command=self._start
        )

        # Stop
        stop_button = Button(
            main_frame,
            text='停止',
            relief='solid',
            borderwidth=1,
            command=self._stop
        )

        # Log
        log_label = Label(main_frame, text='ログ')
        log_box = Text(
            main_frame,
            relief='solid',
            borderwidth=1,
            background='#121212',
            foreground='#ffffff',
            wrap=None
        )
        log_box.bind('<Key>', lambda e: "break")
        self.log_box = log_box
        # Set text color in the log box
        self.log_box.tag_configure('log_time', foreground='#43d8c9')
        for log_status in LogStatus:
            self.log_box.tag_configure(log_status.name, foreground=log_status.value)

        # Log scroll bar
        scrollbar_vertical = Scrollbar(
            main_frame,
            orient=VERTICAL,
            command=log_box.yview
        )
        log_box.configure(yscrollcommand=scrollbar_vertical.set)

        # Clear log
        log_clear_button = Button(
            main_frame,
            text='ログをクリア',
            relief='solid',
            borderwidth=1,
            command=self._clear_log
        )

        # Export log
        log_export_button = Button(
            main_frame,
            text='ログを出力',
            relief='solid',
            borderwidth=1,
            command=self._export_log
        )

        # Place all widgets
        dir_to_watch_label.grid(
            row=0, column=0, sticky=W, padx=(0, 7), pady=(10, 10)
        )
        dir_to_watch_entry.grid(
            row=0, column=1, sticky=EW, padx=(10, 10), pady=(10, 10)
        )
        dir_to_watch_button.grid(
            row=0, column=2, padx=(7, 0), pady=(10, 10)
        )

        output_dir_label.grid(
            row=1, column=0, sticky=W, padx=(0, 7), pady=(10, 10)
        )
        output_dir_entry.grid(
            row=1, column=1, sticky=EW, padx=(10, 10), pady=(10, 10)
        )
        output_dir_button.grid(
            row=1, column=2, padx=(7, 0), pady=(10, 10)
        )

        file_type_label.grid(
            row=2, column=0, sticky=W, padx=(0, 7), pady=(10, 10)
        )
        file_type_combobox.grid(
            row=2, column=1, columnspan=2, sticky=EW, padx=(7, 0), pady=(10, 10)
        )

        execute_button.grid(
            row=3, column=0, columnspan=3, pady=(10, 20)
        )

        stop_button.grid(
            row=4, column=0, columnspan=3, pady=(10, 20)
        )

        log_label.grid(
            row=5, column=0, sticky=W, pady=(7, 0)
        )
        log_clear_button.grid(
            row=5, column=1, sticky=E, padx=(0, 10), pady=(0, 7)
        )
        log_export_button.grid(
            row=5, column=2, sticky=E, pady=(0, 7)
        )
        log_box.grid(
            row=6, column=0, columnspan=3, sticky=NSEW
        )
        scrollbar_vertical.grid(
            row=6, column=1, columnspan=2, sticky=(N, S, E), padx=(1, 1), pady=(1, 1)
        )

        # Fit the main frame to master
        self.grid_rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def _start(self):
        """実行

        実行を押下したときの動作内容
        入力パラメータがあっているか，
        監視スレッドがすでに生きているかをチェックする

        """
        try:
            validate_dir(self.watch_dir_path.get(), '監視')
            validate_dir(self.output_dir_path.get(), '出力')
            validate_file_type(self.file_type.get())
        except ValidateError as e:
            messagebox.showerror(e.args[0], e.args[1])
            return

        # If the watcher thread is running, show the message box
        if watcher_thread_is_alive(self.watcher_thread):
            switching_watcher = messagebox.askyesnocancel(
                'エラー',
                'すでに実行中です\n監視しているディレクトリを切り替えますか?'
            )
            # If the user select no or cancel, return
            if not switching_watcher:
                return
            # If the user select yes, stop the watcher thread which exists
            self._stop()
        else:
            # If the watcher thread is not running, show the message
            start_observing = messagebox.askyesnocancel(
                '監視',
                '監視を始めますか?'
            )
            if not start_observing:
                return

        self.watcher_thread = Watcher(
            queue=self.queue,
            input_path=self.watch_dir_path.get(),
            output_path=self.output_dir_path.get(),
            extensions=[self.file_type.get()],
        )
        self.watcher_thread.start()
        self.after(100, self._insert_to_log_box)

    def _stop(self):
        """停止

        停止を押下したときの動作内容
        監視スレッドが死んでいる場合は，メッセージを表示する

        """
        # If the watcher thread exists, stop the thread
        if watcher_thread_is_alive(self.watcher_thread):
            self.watcher_thread.stop_event()
            self.watcher_thread.join()
            self.after(100, self._insert_to_log_box)
        else:
            # Show a message box, when watcher thread does not exist
            messagebox.showwarning(
                'エラー',
                '実行されていないため停止することができません\n実行を行ったうえで停止することができます'
            )

    def _insert_to_log_box(self):
        """ログにメッセージを追加

        ログにメッセージを色付きで追加する

        """
        # If queue is not empty, insert message to log box
        if not self.queue.empty():
            # Time
            log_time = '[' + datetime.now().strftime('%Y/%m/%d_%H:%M:%S') + '] '
            self.log_box.insert(
                'end',
                log_time,
                'log_time'
            )

            message_queue = self.queue.get()
            # Status
            log_status_message = f'<{message_queue.status.name}> '
            self.log_box.insert(
                'end',
                log_status_message,
                f'{message_queue.status.name}'
            )

            # Message
            log_message = message_queue.message + '\n'
            self.log_box.insert(
                'end',
                log_message
            )

            # If the log status was completed, return
            if message_queue.status is LogStatus.COMPLETED:
                return

        # Recursively call function for always checking the queue is empty or not
        if watcher_thread_is_alive(self.watcher_thread):
            self.after(100, self._insert_to_log_box)

    def _clear_log(self):
        """ログクリア

        ログをクリアを押下することで，
        ログに表示されているものを全て削除する

        """
        self.log_box.delete('1.0', 'end')

    def _export_log(self):
        """ログ出力

        ログを出力を押下することで，
        ユーザが選択したディレクトリに保存する

        """
        dir_name = filedialog.Directory().show()
        if not dir_name:
            return

        filename = datetime.now().strftime('%Y%m%d_%H%M%S_LOG.txt')
        will_save = messagebox.askyesnocancel(
            '保存',
            f'{filename}で保存します\n続行しますか?'
        )
        if not will_save:
            return

        # Get all text in the log box
        log_text = self.log_box.get(1.0, 'end-1c')
        with open(file=f'{dir_name}/{filename}', mode='w', encoding='utf-8') as f:
            f.write(log_text)

    def _exit_app(self):
        """アプリ終了

        xボタンを押下し，
        監視スレッドが生きている場合はメッセージを表示し，
        スレッドを正常終了させて，アプリを閉じる

        """
        _exit = messagebox.askyesnocancel(
            '終了',
            '処理を終了しますか?'
        )
        if not _exit:
            return

        if watcher_thread_is_alive(self.watcher_thread):
            self._stop()
        self.master.destroy()

    @classmethod
    def get_instance(cls, master=ROOT):
        """アプリのインスタンス取得

        BookMakerAppのインスタンスを返す

        """
        if not hasattr(cls, '_instance'):
            cls._instance = cls(master)
        else:
            cls._instance.master = master
        return cls._instance


def main():
    global ROOT
    app = BookMakerApp(ROOT)
    app.mainloop()


if __name__ == '__main__':
    main()
