#!/usr/bin/env pipenv-shebang
import sys
import logging

import yaml

import main as _
from imagehandler import download_notice, edit_notice, print_file


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
                print_file(edited_filepath)
                logger.debug(
                    "%s %s print an image %s",
                    chat_id,
                    petugas,
                    edited_filename,
                )
            else:
                logger.debug("error on edit image")
        else:
            logger.debug("error on download image")


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    main()
