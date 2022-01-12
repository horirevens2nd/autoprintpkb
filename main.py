#!/usr/bin/env pipenv-shebang
import os
import logging
import logging.config

import pretty_errors
import yaml

OFFICE = "KANTOR POS NGANJUK 64400"

# init directories
LOG_DIR = "./log"
DIST_DIR = "./dist"
ETBPKP_DIR = "./dist/etbpkp"
ORIGINAL_DIR = "./dist/etbpkp/original"
EDITED_DIR = "./dist/etbpkp/edited"
REPORT_DIR = "./dist/report"

dirpaths = [LOG_DIR, DIST_DIR, ETBPKP_DIR, ORIGINAL_DIR, EDITED_DIR, REPORT_DIR]
for dirpath in dirpaths:
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)


# init logger
with open("logging.yaml", "r") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
logging.config.dictConfig(config)
