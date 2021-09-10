#!/usr/bin/env pipenv-shebang
import sys
import logging

import yaml

import main as _
from telegrambot import (
    send_message,
    send_document_,
    registered_users,
    registered_admins,
)
from imagehandler import download_notice, edit_notice, print_file
from sqlitehandler import create_connection, execute_one, fetch_one


def main():
    if len(sys.argv) == 9:
        chat_id = sys.argv[1]
        no_polisi = sys.argv[2]
        bsu = sys.argv[3]
        idtrans = sys.argv[4]
        idsah = sys.argv[5]
        url = sys.argv[6]
        petugas = sys.argv[7]
        waktu = sys.argv[8]

        # download, edit and print image
        original_filename, original_filepath = download_notice(no_polisi, url)
        if original_filename is not None:
            edited_filename, edited_filepath = edit_notice(
                original_filename, original_filepath, petugas, waktu, url
            )
            if edited_filename is not None:
                # insert into table printrequest
                values = (no_polisi, idtrans, idsah, bsu, url, waktu, petugas)
                sql = """INSERT OR REPLACE INTO printrequest VALUES (?, ?, ?, ?, ?, ?, ?)"""
                conn = create_connection()
                if conn is not None:
                    rows = execute_one(conn, sql, values)
                    conn.close()
                    logger.info("insert %s data into database", rows)

                print_file(edited_filepath)
                logger.info(
                    "%s %s print an image %s",
                    chat_id,
                    petugas,
                    edited_filename,
                )

                # send message to user
                message = (
                    f"Pajak Kendaraan Bermotor dengan nomor polisi {no_polisi} sudah dicetak. "
                    "Terima kasih"
                )
                send_message(chat_id, message)

                # send message to admins
                message2 = f"{petugas} mencetak Pajak Kendaraan Bermotor dengan nomor polisi {no_polisi}"
                for chat_id in registered_admins.keys():
                    send_message(chat_id, message2)
            else:
                message = (
                    "Terjadi kesalahan saat proses ubah gambar Pajak Kendaraan Bermotor. "
                    "Silakan dicoba kembali"
                )
                send_message(chat_id, message)
        else:
            message = (
                f"Terjadi kesalahan saat mengunduh gambar Pajak Kendaraan Bermotor dari {url}. "
                "Silakan dicoba kembali"
            )
            send_message(chat_id, message)
    elif len(sys.argv) == 5:
        # read from database using no_polisi
        chat_id = sys.argv[1]
        no_polisi = f"{sys.argv[2]} {sys.argv[3]} {sys.argv[4]}"
        values = (no_polisi,)
        sql = """SELECT * FROM printrequest WHERE no_polisi = ?"""
        conn = create_connection()
        if conn is not None:
            record = fetch_one(conn, sql, values)
            if record is not None:
                no_polisi = record[0]
                url = record[4]
                petugas = record[6]
                waktu = record[5]
                conn.close()

                # download, edit and print image
                original_filename, original_filepath = download_notice(no_polisi, url)
                if original_filename is not None:
                    edited_filename, edited_filepath = edit_notice(
                        original_filename, original_filepath, petugas, waktu, url
                    )
                    if edited_filename is not None:
                        print_file(edited_filepath)
                        logger.info(
                            "%s %s print an image %s",
                            chat_id,
                            petugas,
                            edited_filename,
                        )

                        # send message to user
                        message = (
                            f"Pajak Kendaraan Bermotor dengan nomor polisi {no_polisi} sudah dicetak. "
                            "Terima kasih"
                        )
                        send_message(chat_id, message)
                    else:
                        message = (
                            "Terjadi kesalahan saat proses ubah gambar Pajak Kendaraan Bermotor. "
                            "Silakan dicoba kembali"
                        )
                        send_message(chat_id, message)
                else:
                    message = (
                        f"Terjadi kesalahan saat mengunduh gambar Pajak Kendaraan Bermotor dari {url}. "
                        "Silakan dicoba kembali"
                    )
                    send_message(chat_id, message)
            else:
                message = f"Nomor polisi {no_polisi} tidak ditemukan"
                send_message(chat_id, message)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    main()
