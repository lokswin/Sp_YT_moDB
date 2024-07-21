import logging

class Logger:
    """
    A simple logging utility for debugging and informational messages.

    Attributes:
        logger (logging.Logger): The logger instance configured with handlers and formatters.
    """

    def __init__(self, debug_mode=False):
        """
        Initializes the Logger with optional debug mode.

        Args:
            debug_mode (bool, optional): Whether to enable debug mode. Defaults to False.
        """
        self.logger = logging.getLogger("My_iLogger")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.set_debug_mode(debug_mode)
        self.debug_mode = debug_mode

    def set_debug_mode(self, debug_mode):
        """
        Sets the logging level based on whether debug mode is enabled.

        Args:
            debug_mode (bool): Whether to enable debug mode.
        """
        self.debug_mode = debug_mode
        self.logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)

    def debug(self, message):
        """
        Logs a debug message.

        Args:
            message (str): The debug message to log.
        """
        self.logger.debug(message)

    def info(self, message):
        """
        Logs an informational message.

        Args:
            message (str): The informational message to log.
        """
        self.logger.info(message)

    def error(self, message):
        """
        Logs an error message.

        Args:
            message (str): The error message to log.
        """
        self.logger.error(message)
