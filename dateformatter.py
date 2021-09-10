def format_1(date):
    """return new date format (01 Januari 2021)

    :param date: yyyymmdd
    :return: dd MM yyyy
    """
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]

    if month == "01":
        month = "Januari"
    elif month == "02":
        month = "Februari"
    elif month == "03":
        month = "Maret"
    elif month == "04":
        month = "April"
    elif month == "05":
        month = "Mei"
    elif month == "06":
        month = "Juni"
    elif month == "07":
        month = "Juli"
    elif month == "08":
        month = "Agustus"
    elif month == "09":
        month = "September"
    elif month == "10":
        month = "Oktober"
    elif month == "11":
        month = "November"
    elif month == "12":
        month = "Desember"
    return f"{day} {month} {year}"


def format_2(date, separator):
    """return new format 2021-01-01

    :param date: yyyymmdd
    :param separator: separator
    :return: yyyy-mm-dd
    """
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    return year + separator + month + separator + day


def format_3(date, separator):
    """return new format 2021-01-01

    :param date: dd/mm/yyyy
    :param separator: separator
    :return: yyyy-mm-dd
    """
    year = date[6:10]
    month = date[3:5]
    day = date[0:2]
    return year + separator + month + separator + day
