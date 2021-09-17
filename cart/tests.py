import sqlite3
from sqlite3 import Error

database = r"../db.sqlite3"

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def select_all_tables(conn):
    cur = conn.cursor()
    #cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    cur.execute("SELECT * FROM pragma_table_info('onlineshop_produit')")

    rows = cur.fetchall()

    for row in rows:
        print(row)


def main():
    conn = create_connection(database)
    with conn:
        select_all_tables(conn)


if __name__ == '__main__':
    main()
