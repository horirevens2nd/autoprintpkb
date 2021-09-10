#!/usr/bin/env pipenv-shebang
import os
import logging

import pretty_errors
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from PIL import Image, ImageFont, ImageDraw, ImageOps

from filehandler import create_dirs, create_subdirs


def driver():
    path = os.path.join(os.path.dirname(__file__), "chromedriver")
    options = Options()
    options.add_argument("--headless")
    return webdriver.Chrome(options=options, executable_path=path)


def download_notice(nopol, url):
    filename = f"{nopol.replace(' ', '')}.png"
    dist_dirpath = create_dirs(["dist"])
    image_dirpath = create_subdirs(dist_dirpath[0], ["image"])
    original_dirpath = create_subdirs(image_dirpath[0], ["original"])
    filepath = os.path.join(original_dirpath[0], filename)

    try:
        driver.get(url)
        image = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "img"))
        )
        image.screenshot(filepath)
        logger.info("file %s is downloaded", filename)
        driver.quit()
    except (TimeoutException) as e:
        logger.exception(e)
        filename, filepath = None, None
        driver.quit()
    except (NoSuchElementException) as e:
        logger.exception(e)
        filename, filepath = None, None
        driver.quit()
    return filename, filepath


def edit_notice(filename_source, filepath_source, petugas, waktu, url):
    if os.path.isfile(filepath_source):
        splited = filename_source.split(".")
        filename = f"{splited[0]}_.png"
        dist_dirpath = create_dirs(["dist"])
        image_dirpath = create_subdirs(dist_dirpath[0], ["image"])
        edited_dirpath = create_subdirs(image_dirpath[0], ["edited"])
        filepath = os.path.join(edited_dirpath[0], filename)

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
            text="PT POS INDONESIA (PERSERO)\nKantor Pos Nganjuk 64400",
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
    filename = os.path.basename(filepath)
    logger.info("file %s is printed", filename)


if __name__ != "__main__":
    logger = logging.getLogger(__name__)
    driver = driver()
