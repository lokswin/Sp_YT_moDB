# file: app/logger_class.py
import logging

class Logger:
    def __init__(self, debug_mode=False):
        self.logger = logging.getLogger("MyLogger")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.set_debug_mode(debug_mode)
        self.debug_mode = debug_mode
        self.gui_log_widget = None

    def set_debug_mode(self, debug_mode):
        self.debug_mode = debug_mode
        self.logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)

    def set_gui_log_widget(self, log_widget):
        self.gui_log_widget = log_widget

    def log_to_gui(self, message):
        if self.gui_log_widget:
            self.gui_log_widget.configure(state='normal')
            self.gui_log_widget.insert(tk.END, message + "\n")
            self.gui_log_widget.configure(state='disabled')
            self.gui_log_widget.see(tk.END)

    def debug(self, message):
        self.logger.debug(message)
        if self.debug_mode:
            self.log_to_gui(message)

    def info(self, message):
        self.logger.info(message)
        self.log_to_gui(message)

    def error(self, message):
        self.logger.error(message)
        self.log_to_gui(message)
