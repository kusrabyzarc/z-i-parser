import csv
import os
import sqlite3
import sys
import yaml
import logger_module
import io

with open('config.yml') as f:
    config = yaml.safe_load(f.read())

logger = logger_module.create_logger(__name__)


def reinit_db():
    if os.path.exists(config['db_name']):
        logger.info('Найдена старая база данных, удаляем...')
        os.remove(config['db_name'])

    maxInt = sys.maxsize
    while True:
        try:
            csv.field_size_limit(maxInt)
            logger.debug(f'Установлен максимальный размер csv ячеек: {maxInt}')
            break
        except OverflowError:
            maxInt = int(maxInt / 2)


def connect_db():
    conn = sqlite3.connect(config['db_name'])
    logger.debug(f'Подключились к базе {config["db_name"]}.')
    cursor = conn.cursor()
    create_table_sql = '''CREATE TABLE write(
        ip TEXT,
        url TEXT,
        page TEXT,
        law TEXT,
        cause TEXT,
        date TEXT);
    '''
    cursor.execute(create_table_sql)
    return conn, cursor

def insert_data(filename, cursor, connection):
    file_size = os.path.getsize(filename)
    if file_size == 0:
        logger.warning('Файл пуст.')
        return

    insert_sql = 'INSERT INTO write (ip, url, page, law, cause, date) VALUES (?, ?, ?, ?, ?, ?)'
    batch = []
    total_inserted = 0

    block_size = config['reader_block_size']

    with open(filename, 'rb') as raw:
        with io.TextIOWrapper(raw, encoding='utf-8') as f:
            data = csv.reader(f, delimiter=';')
            next(data, None)  # пропускаем заголовок

            for row in data:
                batch.append(row)
                if len(batch) >= block_size:
                    cursor.executemany(insert_sql, batch)
                    connection.commit()
                    total_inserted += len(batch)
                    percent = (raw.tell() / file_size) * 100
                    logger.info(f'Вставлено {total_inserted} записей (~{percent:.2f}%)...')
                    batch.clear()

            if batch:
                cursor.executemany(insert_sql, batch)
                connection.commit()
                total_inserted += len(batch)
                percent = (raw.tell() / file_size) * 100
                logger.info(f'Вставлено {total_inserted} записей (~{percent:.2f}%).')



if __name__ == '__main__':
    reinit_db()
    conn, cur = connect_db()
    insert_data('dumps\\dump.csv', cur, conn)
    conn.close()
