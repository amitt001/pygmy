import logging
import threading

from pygmy.config import config


class Logger:
    """Configure singleton logger for application and return its instance."""
    _lock = threading.Lock()
    _instance = None

    def __new__(cls, filename=None, level=logging.DEBUG, format=None):
        log_config = {'level': getattr(logging, level, logging.DEBUG)}
        if filename:
            log_config.update({'filename': filename})
        if format:
            log_config.update({'format': format})

        with cls._lock:
            if cls._instance is None:
                logging.basicConfig(**log_config)
                logger = logging.getLogger(__name__)
                cls._instance = logger
                cls._instance.info('Logger created for {}'.format(__name__))
                cls._add_stream_handler(level, format)

        cls._instance.info('Logging setup done for {}'.format(__name__))
        return cls._instance

    @classmethod
    def _add_stream_handler(cls, level, format):
        cls._instance.info('Adding stream handler to logger')
        handler = logging.StreamHandler()
        handler.setLevel(level)
        if format:
            formatter = logging.Formatter(format)
            handler.setFormatter(formatter)
        cls._instance.addHandler(handler)


log = Logger(config.logging['filepath'], config.logging['level'], config.logging['format'])
