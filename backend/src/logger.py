import logging


class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # create a file handler
        handler = logging.FileHandler("log.txt")
        handler.setFormatter(
            logging.Formatter("%(asctime)s:%(name)s: %(levelname)s: %(message)s")
        )
        self.logger.addHandler(handler)

        # create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s: %(name)s: %(levelname)s: %(message)s")
        )
        self.logger.addHandler(console_handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)
