#!/usr/bin/env pipenv-shebang
import os
import logging
import datetime

import yaml

import main as _
from sqlitehandler import create_connection, fetch_all


def main():
    today = datetime.date.today()
    values = (f"{today}%",)
    sql = "SELECT * FROM printrequest WHERE waktu LIKE ?"
    conn = create_connection()
    if conn is not None:
        records = fetch_all(conn, sql, values)
        conn.close()

    for record in records:
        chat_id = 159508674
        no_polisi = record[0]
        no_polisi = no_polisi.replace(" ", "\ ")
        id_trans = record[1]
        id_sah = record[2]
        bsu = record[3]
        url = record[4]
        waktu = record[5].replace(" ", "\ ")
        petugas = record[6].replace(" ", "\ ")

        command = (
            f"pipenv-shebang printrequest2nd.py {chat_id} {no_polisi} {bsu} "
            f"{id_trans} {id_sah} {url} {petugas} {waktu}"
        )
        os.system(command)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    main()
