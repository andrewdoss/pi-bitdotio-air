import logging
import os
import serial
import sys
import time

import bitdotio
from dotenv import load_dotenv
import yaml

load_dotenv()
BITDOTIO_API_KEY = os.getenv('BITDOTIO_API_KEY')


logging.basicConfig(
    filename='log.out',
    filemode='a',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def parse_value(data, start_byte, num_bytes):
    value = data[start_byte: start_byte + num_bytes]
    return int.from_bytes(value, byteorder='little')


def parse_measurement(data, start_byte, num_bytes, denom):
    return parse_value(data, start_byte, num_bytes) / denom


def execute_sql(bitdotio, sql, params=None):
    '''Run arbitrary SQL statements on bitdotio'''
    try:
        conn = bitdotio.get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        cur.close()
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


def insert_record(bitdotio, record, CONFIG):
    repo_owner = CONFIG['repo_owner']
    repo_name = CONFIG['repo_name']
    table_name = CONFIG['table_name']
    fully_qualified = f'"{repo_owner}/{repo_name}"."{table_name}"'
    sql = f'INSERT INTO {fully_qualified} '
    sql += 'VALUES (DEFAULT, ' + ', '.join(['%s'] * len(record)) + ');'
    execute_sql(bitdotio, sql, record)


def main():
    with open('config.yaml', 'r') as f:
        CONFIG = yaml.safe_load(f)

    ser = serial.Serial('/dev/ttyUSB0')

    b = bitdotio.bitdotio(BITDOTIO_API_KEY)
    
    while True:
        sample = [ser.read(10) for i in range(CONFIG['period'])]

        record = {'location': CONFIG['location']}

        record['sensor_id'] = parse_value(sample[0], *CONFIG['sensor_id'])
        for measurement, parse_args in CONFIG['measurements'].items():
            meas_sum = sum([parse_measurement(x, *parse_args) for x in sample])
            record[measurement] = meas_sum / CONFIG['period']

        insert_record(b, [record[col] for col in CONFIG['columns']], CONFIG)
        logging.info(f'RECORD UPLOADED: {record}')


if __name__ == '__main__':
    main()
