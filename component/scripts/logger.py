import sys
import logging
from pathlib import Path
import colorlog  # Install via: pip install colorlog

# ANSI background color codes
BLUE_BG = "\033[44m"
PURPLE_BG = "\033[45m"
YELLOW_BG = "\033[43m"
RESET = "\033[0m"


class CustomLogger:
    def __init__(
        self,
        name: str,
        level: int = logging.DEBUG,
        module_color: str = BLUE_BG,
        log_file: str | Path | None = None,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create a colored console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Build the format string using the module_color for the logger's name
        format_str = f"%(log_color)s%(asctime)s - {module_color}%(name)s{RESET} - %(levelname)s - %(message)s"
        console_formatter = colorlog.ColoredFormatter(
            format_str,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Add file handler if log_file is specified
        if log_file:
            log_file = Path(log_file)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def message_to_string(self, *messages: str) -> str:
        return " ".join(str(msg) for msg in messages)

    def debug(self, *messages: str):
        self.logger.debug(self.message_to_string(*messages))

    def info(self, *messages: str):
        self.logger.info(self.message_to_string(*messages))

    def warning(self, *messages: str):
        self.logger.warning(self.message_to_string(*messages))

    def error(self, *messages: str):
        self.logger.error(self.message_to_string(*messages))

    def critical(self, *messages: str):
        self.logger.critical(self.message_to_string(*messages))


logger = CustomLogger(
    "FIRES", module_color=BLUE_BG, log_file="/home/dguerrero/fires.log"
)
