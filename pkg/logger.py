import sys

import os


from loguru import logger


class Logger:
    """
    Класс для настройки логгера.
    """

    LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>"
    COMPRESSION = "zip"
    ROTATION = "100 MB"
    DEBUG = "debug"
    INFO = "info"

    def __init__(
        self,
        log_level: str,
        log_dir_name: str,
        info_log_path: str | None = None,
        debug_log_path: str | None = None,
    ):
        self.log_level = log_level
        self.log_dir_name = log_dir_name
        self.info_log_path = info_log_path
        self.debug_log_path = debug_log_path

    def create_log_directory_if_exists(self) -> None:
        """
        Создание директории с логами, если нет.
        :return:
        """
        if not os.path.exists(self.log_dir_name):
            os.makedirs(self.log_dir_name, exist_ok=True)

    def setup_logger(self) -> None:
        """
        Настройка и распределение логов.
        :return:
        """
        self.create_log_directory_if_exists()
        match self.log_level:
            case self.DEBUG:
                log_path = self.debug_log_path
            case self.INFO:
                log_path = self.info_log_path
            case _:
                raise ValueError(f"Invalid log level: {self.log_level}")

        logger.remove()

        logger.add(
            log_path,
            format=self.LOG_FORMAT,
            level=self.log_level.upper(),
            rotation=self.ROTATION,
            compression=self.COMPRESSION,
        )

        logger.add(
            sys.stdout,
            format=self.LOG_FORMAT,
            level=self.log_level.upper(),
        )
