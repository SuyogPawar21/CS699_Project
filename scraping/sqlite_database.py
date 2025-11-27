import sqlite3
import json
import csv
import sys
import os

def create_db(table_name):
    connector = sqlite3.connect("static/Papers_data.db")
    connector_cursor = connector.cursor()

    connector_cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS \"{table_name}\" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            author TEXT,
            citations INTEGER,
            keywords TEXT
        )
    """)

    connector.commit()
    connector.close()


def insert_paper(name, author, citations, keywords_list, table_name):
    create_db(table_name)
    connector = sqlite3.connect("static/Papers_data.db")
    connector_cursor = connector.cursor()

    keywords_json = json.dumps(keywords_list)
    author_json = json.dumps(author)

    connector_cursor.execute(f"""
        INSERT INTO \"{table_name}\" (name, author, citations, keywords)
        VALUES (?, ?, ?, ?)""",(name, author_json, citations, keywords_json))

    connector.commit()
    connector.close()


def merge_tables(final_table, all_tables, csv_path="files/Final_Data.csv"):
    connector = sqlite3.connect("static/Papers_data.db")
    connector_cursor = connector.cursor()

    connector_cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS "{final_table}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            author TEXT,
            citations INTEGER,
            keywords TEXT
        );""")

    for tb in all_tables:
        query = f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{tb}';"""
        connector_cursor.execute(query)
        result = connector_cursor.fetchone()

        if(result):
            connector_cursor.execute(f"""INSERT INTO "{final_table}" (name, author, citations, keywords) SELECT name, author, citations, keywords FROM "{tb}";""")
    print(f"{all_tables} Merged into {final_table}")
    connector.commit()

    connector_cursor.execute(f"""SELECT * FROM "{final_table}";""")
    rows = connector_cursor.fetchall()
    column_names = [X[0] for X in connector_cursor.description]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(column_names)
        writer.writerows(rows)

    connector.close()
    print(f"CSV created at: {csv_path}")

