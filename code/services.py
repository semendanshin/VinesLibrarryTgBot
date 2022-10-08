from logging import getLogger
from logging import config
from config import LOGGING
from datetime import datetime
import subprocess


config.dictConfig(LOGGING)
logger = getLogger(__name__)


def debug(f):
    """Декоратор логирования"""
    def inner(*args, **kwargs):
        try:
            logger.info(f'Обращение в функцию {f.__name__}')
            return f(*args, **kwargs)
        except Exception as e:
            logger.exception(f'Ошибка - {e}')
            subprocess.call(['python', 'main.py'])
    return inner


@debug
def save_image(image: bytes) -> str:
    """Сохраниет изображение и возварщает имя файла"""
    name = str(datetime.now()).replace('-', '').replace(':', '').replace('.', '').replace(' ', '') + '.jpg'
    with open(f'data/img/{name}', 'wb') as f:
        f.write(image)
    return name
