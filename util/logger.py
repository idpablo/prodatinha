import logging

class LoggingFormatter(logging.Formatter):
    
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record): # pyright: ignore
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<0}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%d-%m-%Y %H:%M:%S", style="{")
        return formatter.format(record)

def setup_logger(logger_name: str,  log_file: str = 'log/discord.log'):

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(LoggingFormatter())
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(filename=log_file, encoding="utf-8", mode="a")
    file_handler_formatter = logging.Formatter(
        "[{asctime}] [{levelname:<0}] {name}: {message}", "%d-%m-%Y %H:%M:%S", style="{"
    )
    file_handler.setFormatter(file_handler_formatter)
    logger.addHandler(file_handler)

    return logger
