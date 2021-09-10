#!/usr/bin/env pipenv-shebang
import os
import logging
import logging.config

import pretty_errors
import yaml

# init base directories
names = ["dist", "log"]
for name in names:
    path = os.path.join(os.path.dirname(__file__), name)
    if not os.path.isdir(path):
        os.mkdir(path)

# init logger
with open("logging.yaml", "r") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
logging.config.dictConfig(config)
