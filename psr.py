#!/usr/bin/python
import psycopg2
import configurations
import sys

def process_columns(conn, cur, columns):
    for schema in columns:
        for table in schema[1]:
            for column in table[1]:
                process_column(conn, cur, schema[0], table[0], column)

def process_column(conn, cur, schema, table, column):
    cur.execute(generate_select(schema, table, column, sys.argv[2]))
    rows = cur.fetchall()

    for row in rows:
        print_row(schema, table, column, row[0])

    if rows and len(sys.argv) > 3:
        if input_search_replace(len(rows)):
            cur.execute(generate_update(schema, table, column, sys.argv[2], sys.argv[3]))
            conn.commit()

def generate_select(schema, table, column, search_str):
    return 'select {2} from {0}.{1} where {2} like \'%{3}%\';'.format(
        schema, table, column, search_str)

def print_row(schema, table, column, value):
    print('{0}.{1}, {2}: {3}\n--'.format(schema, table, column, value))

def input_search_replace(len_of_rows):
    return input('Replace \'{}\' with \'{}\' in {} rows? [y/N] '.format(sys.argv[2], sys.argv[3], len_of_rows)).lower() == 'y'

def generate_update(schema, table, column, search_str, replace_str):
    return 'update {0}.{1} set {2} = replace({2}, \'{3}\', \'{4}\');'.format(
        schema, table, column, search_str, replace_str)

def connect(connection):
    return psycopg2.connect(
        database = connection['database'],
        host = connection['host'],
        password = connection['password'],
        port = connection['port'],
        user = connection['user'])

if __name__ == "__main__":
    if len(sys.argv) <= 2:
        print('{} [configuration_id search_str [replace_str]]'.format(sys.argv[0]))
    else:
        for connection in configurations.configurations[sys.argv[1]]:
            conn = connect(connection)
            cur = conn.cursor()
            process_columns(conn, cur, connection['columns'])
            cur.close()
            conn.close()
