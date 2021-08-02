import logging
import serial
import sys
import time

import bitdotio

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

CONFIG = {
    'columns': [
        'location',
        'sensor_id',
        'pm_2_5',
        'pm_10'],
    'measurements': {
        'pm_2_5': (2, 2, 10),
        'pm_10': (4, 2, 10)
    },
    'sensor_id': (6, 2),
    'period': 60,
    'location': "Andrew's house - inside",
    'repo_owner': 'andrewdoss',
    'repo_name': 'air_quality',
    'table_name': 'pm_measurements'
}

ser = serial.Serial('/dev/ttyUSB0')


def parse_value(data, start_byte, num_bytes):
    value = data[start_byte: start_byte + num_bytes]
    return int.from_bytes(value, byteorder='little')


def parse_measurement(data, start_byte, num_bytes, denom):
    return parse_value(data, start_byte, num_bytes) / denom


def execute_sql(bitdotio, sql, params=None):
    '''Run arbitrary SQL statements on bitdotio'''
    try:
        # Connect to bit.io
        conn = bitdotio.get_connection()
        # Open cursor with bit.io server
        cur = conn.cursor()
        # Execute sql
        cur.execute(sql, params)
        # Close cursor
        cur.close()
        # Commit the changes (only relevent for write ops)
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
