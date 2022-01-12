#!/usr/bin/env pipenv-shebang
from __future__ import with_statement
import os
import sys
import logging
import urllib.request

from pdf2image import convert_from_path
from PIL import Image, ImageFont, ImageDraw

import main as _
from telegrambot import (
    send_message,
    send_document_,
    registered_users,
    registered_admins,
)
from sqlitehandler import create_connection, execute_one, fetch_one


def download_notice(no_polisi, url):
    response = urllib.request.urlopen(url)
    filename = f"{no_polisi.replace(' ', '')}.pdf"
    filepath = os.path.join(_.ORIGINAL_DIR, filename)

    try:
        with response, open(filepath, "wb") as f:
            data = response.read()
            f.write(data)
            logger.info("file %s is downloaded", filename)
    except (EnvironmentError) as e:
        logger.exception(e)
        filename, filepath = None, None
    return filename, filepath


def pdf_to_image(filename, filepath):
    pil_image = convert_from_path(
        pdf_path=filepath,
        dpi=300,
        output_folder=_.ORIGINAL_DIR,
        fmt="jpeg",
        single_file=True,
        output_file=os.path.splitext(filename)[0],
    )
    return pil_image


def edit_notice(filepath_source, petugas, waktu, url):
    if os.path.isfile(filepath_source):
        filename_source = os.path.basename(filepath_source)
        splited = filename_source.split(".")
        filename = f"{splited[0]}_.pdf"
        filepath = os.path.join(_.EDITED_DIR, filename)

        image_pkb = Image.open(filepath_source)
        image_pkb = image_pkb.resize((1194, 566))
        ic_pos = Image.open("ic_pos.jpg")
        ic_pos = ic_pos.resize((152, 106))
        lato = ImageFont.truetype("lato_regular.ttf", 22)

        top, bottom, left, right = 268, 284, 196, 196
        width, height = image_pkb.size
        new_width = width + right + left
        new_height = height + top + bottom
        image_edited = Image.new(
            image_pkb.mode, (new_width, new_height), (255, 255, 255)
        )
        image_edited.paste(image_pkb, (left, top))

        draw = ImageDraw.Draw(image_edited)
        draw.text(
            xy=(26, 40),
            text=f"PT POS INDONESIA (PERSERO)\n{_.OFFICE.title()}",
            fill=(0, 0, 0),
            font=lato,
        )
        draw.text(
            xy=(610, 134),
            text="PAJAK KENDARAAN BERMOTOR\nSAMSAT PROVINSI JAWA TIMUR",
            fill=(0, 0, 0),
            font=lato,
            align="center",
        )
        draw.text(
            xy=(26, 222),
            text=f"Petugas : {petugas}",
            fill=(0, 0, 0),
            font=lato,
        )
        draw.text(
            xy=(1228, 222),
            text=f"Tanggal : {waktu}",
            fill=(0, 0, 0),
            font=lato,
            align="center",
        )
        draw.text(
            xy=(0, 242),
            text=" - " * 100,
            fill=(0, 0, 0),
            font=lato,
        )
        draw.text(
            xy=(0, 836),
            text=" - " * 100,
            fill=(0, 0, 0),
            font=lato,
        )
        text_ = (
            f"Pajak Kendaraan Bermotor ini dapat diunduh di {url}\n"
            "Terima Kasih Telah Menggunakan Layanan Kami"
        )
        draw.multiline_text(
            xy=(424, 860),
            text=text_,
            fill=(0, 0, 0),
            font=lato,
            align="center",
        )
        image_edited.paste(ic_pos, (1406, 40))
        image_edited.save(filepath, dpi=(300, 300), quality=95, optimize=True)
        logger.info("file %s is created", filename)
    else:
        filename, filepath = None, None

    return filename, filepath


def print_file(filepath):
    os.system(f"lpr -P Epson-L210-Series_AdminSAP {filepath}")
    # os.system(f"lpr -P L210-Series {filepath}")
    filename = os.path.basename(filepath)
    logger.info("file %s is printed", filename)


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

        # download file
        original_filename, original_filepath = download_notice(no_polisi, url)

        # convert pdf to image
        if original_filename is not None:
            pil_image = pdf_to_image(original_filename, original_filepath)
            pil_filename = pil_image[0].filename

            # edit notice
            edited_filename, edited_filepath = edit_notice(
                pil_filename, petugas, waktu, url
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

                # print_file(edited_filepath)
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

                # download file
                original_filename, original_filepath = download_notice(no_polisi, url)

                # convert pdf to image
                if original_filename is not None:
                    pil_image = pdf_to_image(original_filename, original_filepath)
                    pil_filename = pil_image[0].filename

                    # edit notice
                    edited_filename, edited_filepath = edit_notice(
                        pil_filename, petugas, waktu, url
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
            else:
                message = f"Nomor polisi {no_polisi} tidak ditemukan"
                send_message(chat_id, message)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    main()
