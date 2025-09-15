import logging

# my_logger.debug('This is a debug message.')
# my_logger.info('This is an informational message.')
# my_logger.warning('This is a warning message.')
# my_logger.error('This is an error message.')
# my_logger.critical('This is a critical message!')

def list_to_html_ol(cell):
    if isinstance(cell, list):
        return "<ul>" + "".join(f"<li>{item}</li>" for item in cell) + "</ul>"
    return cell


def strip_json_formatting(text) -> str:
    return text.replace("```json", "").replace("```", "").strip()


def setup_logger(name, log_file, level=logging.INFO):
    """
    Sets up a logger that writes to a specified file and the console.
    """
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create handlers
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create formatters and add them to handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

my_logger = setup_logger("app_logger", "app.log")