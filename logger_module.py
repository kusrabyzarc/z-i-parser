import logging
import yaml
from colorama import Fore, Style, init

with open('config.yml') as f:
    config = yaml.safe_load(f.read())

# Инициализация Colorama для кросс-платформенной поддержки цветов
init(autoreset=True)


class CustomFormatter(logging.Formatter):
    # Определяем цвета для каждого уровня логирования
    COLORS = {
        'DEBUG': Fore.CYAN + Style.BRIGHT,
        'INFO': Fore.GREEN + Style.BRIGHT,
        'WARNING': Fore.YELLOW + Style.BRIGHT,
        'ERROR': Fore.MAGENTA + Style.BRIGHT,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        log_fmt = f"{color}%(asctime)s [%(levelname)s] %(name)s: %(message)s{Style.RESET_ALL}"
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def create_logger(name):
    """
    Создает и возвращает настроенный логгер с заданным названием.

    :param name: str - Название логгера.
    :return: logging.Logger - Настроенный объект логгера.
    """
    logger = logging.getLogger(name)
    logger.setLevel(config['logger_level'])

    # Настраиваем обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Устанавливаем кастомный форматтер
    console_handler.setFormatter(CustomFormatter())

    # Добавляем обработчик в логгер
    logger.addHandler(console_handler)

    return logger


# Примеры использования
if __name__ == '__main__':
    logger = create_logger("example_logger")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning")
    logger.error("This is an error")
    logger.critical("This is critical")
