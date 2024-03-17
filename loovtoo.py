import datetime
import time
from urllib.request import urlretrieve
from requests import get


MITU_ODAVAT = 3
MITU_KALLIST = 3
cheapest_hours = []


def check_date():
    leap_year = 0
    if (
        (praegune_aeg.year % 400 == 0)
        or (praegune_aeg.year % 100 != 0)
        and (praegune_aeg.year % 4 == 0)
    ):
        leap_year = 1
    if (
        praegune_aeg.month == 1
        or praegune_aeg.month == 3
        or praegune_aeg.month == 5
        or praegune_aeg.month == 7
        or praegune_aeg.month == 9
        or praegune_aeg.month == 11
    ):
        if praegune_aeg.day == 31:
            if praegune_aeg.month < 10:
                return "01", f"0{praegune_aeg.month + 1}", praegune_aeg.year
            else:
                return "01", {praegune_aeg.month + 1}, praegune_aeg.year
        if praegune_aeg.day != 31:
            if praegune_aeg.day < 10:
                return praegune_aeg.day + 1, f"0{praegune_aeg.month}", praegune_aeg.year
            else:
                return praegune_aeg.day + 1, praegune_aeg.month, praegune_aeg.year

    if leap_year == 0 and praegune_aeg.month == 2:
        if praegune_aeg.day == 28:
            return "01", f"0{praegune_aeg.month + 1}", praegune_aeg.year
        if praegune_aeg.day != 28 and praegune_aeg.day > 9:
            return praegune_aeg.day, f"0{praegune_aeg.month + 1}", praegune_aeg.year
        if praegune_aeg.day != 28 and praegune_aeg.day < 10:
            return (
                f"0{praegune_aeg.day}",
                f"0{praegune_aeg.month + 1}",
                praegune_aeg.year,
            )

    if leap_year == 1 and praegune_aeg.month == 2:
        if praegune_aeg.day == 29:
            return "01", "03", praegune_aeg.year
        if praegune_aeg.day != 29 and praegune_aeg.day > 9:
            return praegune_aeg.day + 1, f"0{praegune_aeg.month + 1}", praegune_aeg.year
        if praegune_aeg.day != 29 and praegune_aeg.day < 10:
            return (
                f"0{praegune_aeg.day + 1}",
                f"0{praegune_aeg.month + 1}",
                praegune_aeg.year,
            )

    if (
        praegune_aeg.month == 4
        or praegune_aeg.month == 6
        or praegune_aeg.month == 8
        or praegune_aeg.month == 10
    ):
        if praegune_aeg.day == 30:
            return 1, praegune_aeg.month + 1, praegune_aeg.year

        if praegune_aeg.day != 30 and praegune_aeg.day < 10:
            return f"0{praegune_aeg.day + 1}", praegune_aeg.month, praegune_aeg.year
        if praegune_aeg.day != 30 and praegune_aeg.day > 9:
            return praegune_aeg.day, praegune_aeg.month, praegune_aeg.year

    if praegune_aeg.month == 12:
        if praegune_aeg.day == 30:
            return 1, 1, praegune_aeg.year + 1
        if praegune_aeg.day != 30 and praegune_aeg.day < 10:
            return f"0{praegune_aeg.day + 1}", praegune_aeg.month, praegune_aeg.year


def download_file():  # Genereerib lingi ja laeb alla faili
    # Praegune kuupäev
    if praegune_aeg.month < 10:
        kuu = f"0{praegune_aeg.month}"
    else:
        kuu = f"{praegune_aeg.month}"

    if praegune_aeg.day < 10:
        paev = f"0{praegune_aeg.day}"
    else:
        paev = f"{praegune_aeg.day}"

    algus = f"{praegune_aeg.year}-{kuu}-{paev}"

    jj = check_date()
    jpaev = jj[0]
    jkuu = jj[1]
    jaasta = jj[2]

    lõpp = f"{jaasta}-{jkuu}-{jpaev}"

    url = f"https://dashboard.elering.ee/api/nps/price/csv?start={algus}T15%3A00%3A00.000Z&end={lõpp}T15%3A00%3A22.000Z&fields=ee"
    print(url)
    filename = f"export-{praegune_aeg.day}-{praegune_aeg.month}-{praegune_aeg.year}.csv"
    urlretrieve(url=url, filename=filename)


def get_data():  # avab alla laetud faili ja loeb sealt andmed.
    file_info = (
        f"export-{praegune_aeg.day}-{praegune_aeg.month}-{praegune_aeg.year}.csv"
    )
    try:
        with open(file_info, "r") as file:
            lines = file.readlines()[1:]
            data = [line.strip() for line in lines]

    except FileNotFoundError:
        download_file()
        with open(file_info, "r") as file:
            lines = file.readlines()[1:]
            data = [line.strip() for line in lines]

    good_data = []

    for i in range(len(data)):
        new_data = data[i].split(";", 1)[-1]
        good_data.append(new_data)

    return good_data


def correct_data(data):  # Korrigeerib andmed ja sorteerib need
    data_dict = {x.split(";")[0]: x.split(";")[1] for x in data}
    sorted_data = dict(sorted(data_dict.items(), key=lambda item: item[1]))

    char_kustutada = '"'

    for voti in sorted_data:
        sorted_data[voti] = sorted_data[voti].strip(char_kustutada)
        sorted_data[voti] = sorted_data[voti].replace(",", ".")
        sorted_data[voti] = float(sorted_data[voti])

    sorted_data = dict(
        sorted(sorted_data.items(), key=lambda item: item[1]), reverse=True
    )

    return sorted_data


def mis_data_odav(data, mitu_odavat):  # Võtab kõige odavamad andmed
    data = list(data.items())
    new_data = []
    for key in range(mitu_odavat):
        new_data += data[key]
    return new_data


def mis_data_kallis(data, mitu_kallist):  # Võtab kõige kallimad andmed
    data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    new_data = []
    for key in range(mitu_kallist):
        new_data += data[key]
    return new_data


def update_praegune_aeg():  # Tagastab praeguse aja
    return datetime.datetime.now()


def get_ip():  # Loeb serveri ip failist
    try:
        with open("server_ip.txt", "r") as file:
            lines = file.readlines()
            count = 0
            Lines = []
            for line in lines:
                count += 1
                Lines += line.strip()
            return Lines
    except FileNotFoundError:
        open("server_ip.txt", "a")
        with open("server_ip.txt", "r+") as file:
            file.write(input("Sisesta 1. relee ip: "))
            file.write("\n")
            file.write(":::")
            file.write("\n")
            file.write(input("Sisesta releede välja lülitamise ip: "))
            lines = file.readlines()
            count = 0
            Lines = []
            for line in lines:
                count += 1
                Lines += line.strip()
            return Lines


def main():  # Käivitab kõik funktsioonid
    data = get_data()
    data = correct_data(data)
    odav = mis_data_odav(data, MITU_ODAVAT)
    kallis = mis_data_kallis(data, MITU_KALLIST)
    return odav, kallis


a = get_ip()
url_sisse = a[0]
url_valja = a[1]

while True:  # Käivitab kõik funktsioonid
    praegune_aeg = update_praegune_aeg()
    if praegune_aeg.hour == 15:  # Kui kellaaeg on 15:00, siis liigub programm edasi
        download_file()
        odav, kallis = main()
        odavad = {}
        kallid = {}
        for _ in range(MITU_ODAVAT):  # võtab kõige odavamad andmed
            odavad[odav[0]] = odav[1]
            odav.remove(odav[0])
            odav.remove(odav[0])
        print(odavad)

        for _ in range(MITU_KALLIST):  # võtab kõige kallimad andmed
            kallid[kallis[0]] = kallis[1]
            kallis.remove(kallis[0])
            kallis.remove(kallis[0])
        print(kallid)
        while (
            odavad
        ):  # Käivitab relee 1 sisse ja välja lülitamise vastavalt odavatele tundidele
            praegune_aeg = update_praegune_aeg()
            if praegune_aeg.month < 10:
                kuu = f"0{praegune_aeg.month}"
            else:
                kuu = praegune_aeg.month

            if praegune_aeg.day < 10:
                paev = f"0{praegune_aeg.day}"
            else:
                paev = praegune_aeg.day
            date = f'"{paev}.{kuu}.{praegune_aeg.year} {praegune_aeg.hour}:00"'
            if date in odavad:
                get(url=url_sisse)
                print("Relee 1 sisse lülitatud.")
                _ = odavad.pop(date)
                time.sleep(3600)
                print("Relee 1 välja lülitatud.")
                get(url=url_valja)

        time.sleep(10)

    else:  # Kui kellaaeg ei ole 15:00, siis prindib praeguse kellaaja
        print("Current hour is:", praegune_aeg.hour)
        time.sleep(1)
