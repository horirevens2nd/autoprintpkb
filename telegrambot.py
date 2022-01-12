#!/usr/bin/env pipenv-shebang
import os
import sys
import datetime
import logging
import sqlite3
from threading import Thread

import pretty_errors
import yaml
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler

import dateformatter
import main as _
from filehandler import create_report
from sqlitehandler import create_connection, create_table, SQL_TABLE_PRINTREQUEST

# get object from secret.yaml
with open("secret.yaml", "r") as file:
    secret = yaml.load(file, Loader=yaml.FullLoader)
SUPERADMIN_ID = secret["telegram"]["id"]
SUPERADMIN_USERNAME = secret["telegram"]["username"]
PRINTPKB = secret["telegram"]["tokens"]["printpkb"]
USERS = secret["telegram"]["users"]
ADMINS = secret["telegram"]["admins"]

registered_users = {}
for user in USERS:
    user_keyname = list(user)[0]
    user_id = user[user_keyname]["id"]
    user_name = user[user_keyname]["name"]
    registered_users[user_id] = user_name

registered_admins = {}
for admin in ADMINS:
    admin_keyname = list(admin)[0]
    admin_id = admin[admin_keyname]["id"]
    admin_name = admin[admin_keyname]["name"]
    registered_admins[admin_id] = admin_name


updater = Updater(token=PRINTPKB, use_context=True)

# messages
UNREGISTERED = (
    "Anda belum terdaftar. "
    f"Silakan menghubungi {SUPERADMIN_USERNAME} untuk bisa menggunakan bot ini"
)
REGISTERED = (
    "Anda sudah terdaftar. "
    "Silakan kirim format SMS dari SAMSATJATIM seperti contoh dibawah ini:\n\n"
    "Trm kasih pmbyran dan pngsahan STNK AG 1234 ZZ Rp 200.000 "
    "IDTRANS 231210813579xxx 01-01-2025, IDSAH 5608364030821xxx "
    "http://jwtim.id/xxxxxx (WA:081131137070)"
)
SUPERADMIN_ID_COMMAND = (
    "*Bot Command*\n"
    "/getid \- get telelgram ID\n"
    "/getreport \- get report file\n"
    "/print \- print edited image\n"
    "/help \- show this message\n"
    "/restart \- restart the bot\n"
    "/stop \- stop the bot"
)
ADMIN_COMMAND = (
    "*Bot Command*\n"
    "/getid \- get telelgram ID\n"
    "/getreport \- get report file\n"
    "/print \- print edited image\n"
)
PRINT_INVALID_FORMAT = (
    "Argumen yang Anda masukan salah. "
    "Pastikan menggunakan nomor polisi setelah perintah /print\n\n"
    "contoh:\n"
    "/print AG 6207 BD"
)
RESTRICTED = "Anda tidak memiliki akses untuk menjalankan perintah tersebut"


def send_message(chat_id=SUPERADMIN_ID, text="...", parse_mode=None):
    """send message to user"""
    updater.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)


def send_document_(chat_id=SUPERADMIN_ID, filepath=None, caption=None):
    """send document to user"""
    if os.path.isfile(filepath):
        updater.bot.send_document(
            chat_id=chat_id,
            document=open(filepath, "rb"),
            caption=caption,
        )


def read_message(update, context):
    """read message from user"""
    chat_id = update.message.chat.id
    if chat_id in registered_users.keys():
        message = update.message.text
        message = message.split(" ")
        if (len(message) == 18) and (message[14] == "IDSAH"):
            no_polisi = f"{message[6]} {message[7]} {message[8]}"
            no_polisi = no_polisi.replace(" ", "\ ")
            bsu = message[10].replace(".", "")
            id_trans = message[12]
            id_sah = message[15]
            url = message[16]
            petugas = registered_users[chat_id]
            petugas = petugas.replace(" ", "\ ")
            waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            waktu = waktu.replace(" ", "\ ")

            # download, edit and print file
            command = (
                f"pipenv-shebang printrequest.py {chat_id} {no_polisi} {bsu} "
                f"{id_trans} {id_sah} {url} {petugas} {waktu}"
            )
            os.system(command)
        elif (len(message) == 19) and (message[18] == "http://jwtim.id/bpd"):
            message = (
                "Pengesahan STNK hanya bisa dilakukan di SAMSAT. Silakan kirim "
                "dokumen berikut ini agar bisa dibantu untuk proses pengesahaannya:\n"
                "1. STNK Asli\n"
                "2. KTP Asli (harus sesuai dengan nama dan alamat di STNK)\n"
                "3. Resi Pembayaran POSPAY\n"
                "Kirimkan melalui portepel seperti biasanya. Tks"
            )
            update.message.reply_text(message)
        else:
            message = (
                "Format pesan yang Anda kirimkan tidak sesuai. "
                "Silakan kirim format SMS dari SAMSATJATIM seperti contoh dibawah ini:\n\n"
                "Trm kasih pmbyran dan pngsahan STNK AG 1234 ZZ Rp 200.000 "
                "IDTRANS 231210813579xxx 01-01-2025, IDSAH 5608364030821xxx "
                "http://jwtim.id/xxxxxx (WA:081131137070)"
            )
            update.message.reply_text(message)
    else:
        update.message.reply_text(UNREGISTERED)


def get_report(update, context):
    """send {date}_report.xlsx file to user"""
    chat_id = update.message.chat.id
    if chat_id in registered_admins.keys():
        if len(context.args) == 0:
            today = datetime.date.today().strftime("%Y-%m-%d")
            filename, filepath, caption = create_report(today)
            if filename is not None:
                logger.info(
                    "%s %s create report %s",
                    chat_id,
                    registered_admins[chat_id],
                    filename,
                )

                updater.bot.send_document(
                    chat_id=chat_id,
                    document=open(filepath, "rb"),
                    caption=caption,
                )
            else:
                update.message.reply_text(f"file {today}_report.xlsx tidak ditemukan")
        elif len(context.args) == 1:
            today = context.args[0]
            today2 = dateformatter.format_2(today, "-")
            filename, filepath, caption = create_report(today2)
            if filename is not None:
                logger.info(
                    "%s %s create report %s",
                    chat_id,
                    registered_admins[chat_id],
                    filename,
                )

                updater.bot.send_document(
                    chat_id=chat_id,
                    document=open(filepath, "rb"),
                    caption=caption,
                )
            else:
                update.message.reply_text(f"file {today}_report.xlsx tidak ditemukan")
        else:
            message = (
                "Argumen yang Anda masukan salah. "
                "Pastikan menggunakan format YYYYMMDD setelah perintah /getreport\n\n"
                "contoh:\n"
                "/getreport 20210101"
            )
            update.message.reply_text(message)
    else:
        update.message.reply_text(RESTRICTED)


def print(update, context):
    """print edited image to printer"""
    chat_id = update.message.chat.id
    if chat_id in registered_admins.keys():
        if len(context.args) == 0:
            update.message.reply_text(PRINT_INVALID_FORMAT)
        elif len(context.args) == 3:
            # download, edit and print file
            no_polisi = f"{context.args[0]} {context.args[1]} {context.args[2]}"
            command = f"pipenv-shebang printrequest.py {chat_id} {no_polisi}"
            os.system(command)
        else:
            update.message.reply_text(PRINT_INVALID_FORMAT)
    else:
        update.message.reply_text(RESTRICTED)


def start(update, context):
    """send this message"""
    chat_id = update.message.chat.id
    if chat_id == SUPERADMIN_ID:
        update.message.reply_text(SUPERADMIN_ID_COMMAND, parse_mode="MarkdownV2")
    elif chat_id in registered_users.keys():
        update.message.reply_text(REGISTERED)
    elif chat_id in registered_admins.keys():
        update.message.reply_text(ADMIN_COMMAND, parse_mode="MarkdownV2")
    else:
        update.message.reply_text(UNREGISTERED)


def help(update, context):
    """send this message"""
    chat_id = update.message.chat.id
    if chat_id == SUPERADMIN_ID:
        update.message.reply_text(SUPERADMIN_ID_COMMAND, parse_mode="MarkdownV2")
    elif chat_id in registered_users.keys():
        update.message.reply_text(REGISTERED)
    elif chat_id in registered_admins.keys():
        update.message.reply_text(ADMIN_COMMAND, parse_mode="MarkdownV2")
    else:
        update.message.reply_text(UNREGISTERED)


def get_id(update, context):
    """get telegram ID"""
    chat_id = update.message.chat.id
    # first_name = update.message.chat.first_name
    # last_name = update.message.chat.last_name
    # last_name = f" {last_name}" if last_name is not None else ""
    message = (
        f"ID Anda adalah {chat_id}. "
        f"Silakan menghubungi {SUPERADMIN_USERNAME} untuk bisa menggunakan bot ini"
    )
    update.message.reply_text(message)


def stop_and_restart():
    updater.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)


def restart(update, context):
    """restart telegram bot"""
    update.message.reply_text("Bot is restarting...")
    Thread(target=stop_and_restart).start()


def stop_and_shutdown():
    updater.stop()
    updater.is_idle = False


def stop(update, context):
    """stop telegram bot"""
    update.message.reply_text("Bot is shutting down...")
    Thread(target=stop_and_shutdown).start()


def unknown(update, context):
    """send message for unknown command"""
    update.message.reply_text("Perintah yang Anda kirimkan tidak dikenali")


def main():
    # filtered users
    superadmin = Filters.user(username=SUPERADMIN_USERNAME)

    # init handler
    getid_handler = CommandHandler("getid", get_id)
    getreport_handler = CommandHandler("getreport", get_report)
    print_handler = CommandHandler("print", print)
    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", help)
    restart_handler = CommandHandler("restart", restart, filters=superadmin)
    stop_handler = CommandHandler("stop", stop, filters=superadmin)
    read_message_handler = MessageHandler(
        Filters.text & (~Filters.command), read_message
    )
    unknown_handler = MessageHandler(Filters.command, unknown)

    # add handler to dispatcher
    dispatcher = updater.dispatcher
    dispatcher.add_handler(getid_handler)
    dispatcher.add_handler(getreport_handler)
    dispatcher.add_handler(print_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(stop_handler)
    dispatcher.add_handler(read_message_handler)
    dispatcher.add_handler(unknown_handler)

    # start the bot
    updater.bot.send_message(chat_id=SUPERADMIN_ID, text="Bot is starting...")
    updater.start_polling()
    updater.idle()


def init_sqlite():
    try:
        conn = create_connection()
        create_table(conn, SQL_TABLE_PRINTREQUEST)
    except sqlite3.Error as e:
        logger.exception(e)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    init_sqlite()
    main()
