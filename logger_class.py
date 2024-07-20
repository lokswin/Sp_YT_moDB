import logging

class Logger:
    def __init__(self, debug_mode=False):
        self.logger = logging.getLogger("PlaylistLogger")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.debug_mode = debug_mode
        self.set_debug_mode(debug_mode)

    def set_debug_mode(self, debug_mode):
        self.debug_mode = debug_mode
        self.logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)
