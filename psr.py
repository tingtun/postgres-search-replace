#!/usr/bin/python
import psycopg2
import settings
import sys

def process_schemas(db, cur):
    for schema in settings.schemas:
        for table in schema[1]:
            for column in table[1]:
                process_column(db, cur, schema[0], table[0], column)

def process_column(db, cur, schema, table, column):
    cur.execute(generate_select(schema, table, column, sys.argv[1]))
    rows = cur.fetchall()

    for row in rows:
        print_row(schema, table, column, row[0])

    if rows and len(sys.argv) > 2:
        if input_search_replace(len(rows)):
            cur.execute(generate_update(schema, table, column, sys.argv[1], sys.argv[2]))
            db.commit()

def generate_select(schema, table, column, search_str):
    return 'select {2} from {0}.{1} where {2} like \'%{3}%\';'.format(
        schema, table, column, search_str)

def print_row(schema, table, column, value):
    print('{0}.{1}, {2}: {3}\n--'.format(schema, table, column, value))

def input_search_replace(len_of_rows):
    return input('Replace \'{}\' with \'{}\' in {} rows? [y/N] '.format(sys.argv[1], sys.argv[2], len_of_rows)).lower() == 'y'

def generate_update(schema, table, column, search_str, replace_str):
    return 'update {0}.{1} set {2} = replace({2}, \'{3}\', \'{4}\');'.format(
        schema, table, column, search_str, replace_str)

def connect():
    return psycopg2.connect(
        database = settings.database,
        host = settings.host,
        password = settings.password,
        port = settings.port,
        user = settings.user)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('{} [search_str [replace_str]]'.format(sys.argv[0]))
    else:
        db = connect()
        cur = db.cursor()
        process_schemas(db, cur)
        cur.close()
        db.close()
