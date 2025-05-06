import requests
import yaml
import os

import logger_module

logger = logger_module.create_logger(__name__)


def parse_repo_sourceforge() -> dict:
    logger.info('Получение списка файлов...')
    request = requests.get(config['sf_base_url'])
    if request.status_code != 200:
        raise requests.HTTPError('Не 200 код возврата HTTP')
    data = request.content.decode()
    data = data[data.find('<li>'):data.rfind('</li>') + 5]  # Оставляем только часть с файлами/папками
    data = data.split('\n')  # Режем на строки
    data = [i.strip() for i in data]  # Убираем лишние пробелы в начале и в конце
    data = [i[:i.find('</a>')] for i in data]  # Убираем закрывающие тэги
    data = [i[i.rfind('>') + 1:] for i in data]  # Оставляем только названия
    data = [i for i in data if i.endswith('.csv')]  # Оставляем только csv файлы
    links = {i: f'{config['sf_base_url']}{i}' for i in data}
    logger.info('Список файлов получен.')
    logger.debug(f'Файлы: {links}')
    return links  # {'filename': 'http://sf_base_url/filename'}


def file_loader(links: dict) -> None:
    os.makedirs(config['dump_dir'], exist_ok=True)
    for filename, link in links.items():
        logger.info(f'Загрузка файла: {filename}')
        data = requests.get(link).content
        with open(os.path.join(config['dump_dir'], filename), 'wb') as f:
            f.write(data)


def clean() -> None:
    logger.info('Удаление папки дампов...')
    for root, dirs, files in os.walk(config['dump_dir'], topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(config['dump_dir'])



with open('config.yml') as f:
    config = yaml.safe_load(f.read())

if __name__ == '__main__':
    links = parse_repo_sourceforge()
    file_loader(links)
    clean()
