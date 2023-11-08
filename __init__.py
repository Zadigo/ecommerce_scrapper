import logging
import os
import pathlib

import dotenv


PROJECT_PATH = pathlib.Path(__file__).parent.absolute()

dotenv.load_dotenv(PROJECT_PATH / '.env')

URLS_FILE = PROJECT_PATH / os.getenv('urls_file', 'urls.json')


class Logger:
    instance = None

    def __init__(self, name='Ecommerce'):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        logger.addHandler(handler)

        log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M'
        )
        handler.setFormatter(log_format)

        file_handler = logging.FileHandler(PROJECT_PATH / 'access.log')
        logger.addHandler(file_handler)
        file_handler.setFormatter(log_format)

        self.instance = logger

    @classmethod
    def create(cls, name):
        instance = cls(name=name)
        return instance
    
    def warning(self, message, *args, **kwargs):
        self.instance.warning(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self.instance.info(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self.instance.error(message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        self.instance.debug(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self.instance.critical(message, *args, **kwargs)


logger = Logger()
