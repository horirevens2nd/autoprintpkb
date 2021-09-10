import logging.config


class DebugFilter(logging.Filter):
    """get record only from DEBUG tag"""

    def filter(self, record):
        return (
            (record.name == "__main__")
            or (record.name == "filehandler")
            or (record.name == "imagehandler")
            or (record.name == "sqlitehandler")
        )


class InfoFilter(logging.Filter):
    """get record only from INFO tag"""

    def filter(self, record):
        return record.levelname == "INFO"
