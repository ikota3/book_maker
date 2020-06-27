from src.gui.components import BookMakerApp


class LogHandler:

    @staticmethod
    def info(text):
        BookMakerApp.get_instance().insert_to_log_box(text=f'[INFO] {text}')

    @staticmethod
    def warning(text):
        BookMakerApp.insert_to_log_box(text=f'[WARNING] {text}')

    @staticmethod
    def error(text):
        BookMakerApp.insert_to_log_box(text=f'[ERROR] {text}')
