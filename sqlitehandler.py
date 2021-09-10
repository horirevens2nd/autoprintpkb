#!/usr/env/bin pipenv-shebang
import os
import logging
import sqlite3

import main as _


SQL_TABLE_PRINTREQUEST = """CREATE TABLE IF NOT EXISTS printrequest (
    no_polisi TEXT NOT NULL,
    id_trans TEXT NOT NULL,
    id_sah TEXT NOT NULL,
    bsu INTEGER NOT NULL,
    url TEXT NOT NULL,
    waktu TEXT NOT NULL,
    petugas TEXT NOT NULL,
    PRIMARY KEY (id_trans, id_sah)
);"""


def create_connection(filepath="dist/printpkb.db"):
    conn = None
    try:
        conn = sqlite3.connect(filepath)
        return conn
    except sqlite3.Error as e:
        logger.exception(e)
    return conn


def create_table(conn, sql):
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
    except sqlite3.Error as e:
        logger.exception(e)


def execute_one(conn, sql, values=None):
    try:
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        count = cursor.rowcount
        cursor.close()
        return count
    except sqlite3.Error as e:
        logger.exception(e)


def execute_many(conn, sql, values=None):
    try:
        cursor = conn.cursor()
        cursor.executemany(sql, values)
        conn.commit()
        count = cursor.rowcount
        cursor.close()
        return count
    except sqlite3.Error as e:
        logger.exception(e)


def fetch_one(conn, sql, values=None):
    try:
        cursor = conn.cursor()
        cursor.execute(sql, values)
        record = cursor.fetchone()
        cursor.close()
        return record
    except sqlite3.Error as e:
        logger.exception(e)


def fetch_all(conn, sql, values=None):
    try:
        cursor = conn.cursor()
        cursor.execute(sql, values)
        records = cursor.fetchall()
        cursor.close()
        return records
    except sqlite3.Error as e:
        logger.exception(e)


if __name__ != "__main__":
    logger = logging.getLogger(__name__)
