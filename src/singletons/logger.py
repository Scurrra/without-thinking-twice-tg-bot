from typing import Any
import structlog

class Logger:
    """
    Singleton for logging
    """

    _instance: 'Logger' = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._logger = structlog.get_logger()
        return cls._instance._logger