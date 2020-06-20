from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Combobox


class BookMakerApp(Frame):
    """
    Book Maker Application
    """

    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.master.geometry('+1000+100')
        self.master.resizable(0, 0)
        self.master.title('Book Maker')

        self.dir_to_watch_path = StringVar()
        self.log_box_text = StringVar()

        self._create_widgets()

    def _create_widgets(self):
        """
        Create all widgets
        """

        # Main Frame
        main_frame = Frame(self)
        main_frame.grid(row=0, column=0, sticky=NSEW, padx=10, pady=10)

        # Dir to watch
        dir_to_watch_label = Label(main_frame, text='監視対象ディレクトリ')
        dir_to_watch_entry = Entry(
            main_frame,
            relief='solid',
            borderwidth=1,
            textvariable=self.dir_to_watch_path
        )
        dir_to_watch_button = Button(
            main_frame,
            text='参照',
            relief='solid',
            borderwidth=1,
            command=self._ask_folder
        )

        # File type
        file_type_label = Label(main_frame, text='ファイルの種類')
        file_type_combobox = Combobox(main_frame, values=['pdf'])
        file_type_combobox.current(0)

        # Execute
        execute_button = Button(main_frame, text='実行', relief='solid', borderwidth=1, command=self._execute)

        # Text box
        log_label = Label(main_frame, text='ログ')
        log_box = Text(main_frame, relief='solid', borderwidth=1) # TODO bind log_box_text
        log_box.bind('<Key>', lambda e: "break")

        # Place all widgets
        dir_to_watch_label.grid(row=0, column=0, sticky=W, padx=(0, 7), pady=(10, 10))
        dir_to_watch_entry.grid(row=0, column=1, sticky=EW, padx=(10, 10), pady=(10, 10))
        dir_to_watch_button.grid(row=0, column=2, padx=(7, 0), pady=(10, 10))

        file_type_label.grid(row=1, column=0, sticky=W, padx=(0, 7), pady=(10, 10))
        file_type_combobox.grid(row=1, column=1, columnspan=2, sticky=EW, padx=(7, 0), pady=(10, 10))

        execute_button.grid(row=2, column=0, columnspan=3, sticky=NSEW, pady=(10, 20))

        log_label.grid(row=3, column=0, sticky=W, pady=(7, 0))
        log_box.grid(row=4, column=0, columnspan=3, sticky=NSEW)

        # Fit the main frame to master
        self.grid_rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def _ask_folder(self):
        """
        When user clicked "参照"
        Pop up the filedialog for asking directory, and fill the path which user selected
        """
        path = filedialog.askdirectory()
        self.dir_to_watch_path.set(path)

    def _execute(self):
        """
        When user clicked "実行"
        Kick to handler
        """
        print(self.dir_to_watch_path.get())
        # TODO insert all print content to log box
        # TODO colorize

    def _export(self):
        # TODO export the content in the log box
        pass


def main():
    root = Tk()
    app = BookMakerApp(root)
    app.mainloop()


if __name__ == '__main__':
    main()
