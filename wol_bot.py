#! /usr/bin/python3

import socket
import struct
import os

import toml
import telegram_bot_api as api


def config_laden():
    configfile = os.path.join(SKRIPTPFAD, "wol_cfg.toml")
    with open(configfile) as file:
        return toml.loads(file.read())


SKRIPTPFAD = os.path.abspath(os.path.dirname(__file__))
CONFIG = config_laden()


class User:
    def __init__(self, telegramid):
        self.telegramid = telegramid
        self.menue = None
        self.umenue = None


def generate_magic_packet_message(mac_address):
    mac = mac_address.split(":")
    if len(mac) != 6:
        raise ValueError("No correct MAC Address")
    else:
        bin_hardware_address = struct.pack("BBBBBB", *[int(part, 16) for part in mac])
    message = b'\xff' * 6 + bin_hardware_address * 16
    return message


def send_magic_packet(address, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as soc:
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        soc.sendto(message, (address, port))


def sende_verfuegbare_pcs(nachricht, bot, users, telegram_id):
    pc_msg = ""
    for pc in CONFIG["known_computers"].keys():
        pc_msg = f"{pc_msg}\n/{pc}"
    bot.send_message(telegram_id, pc_msg)
    users[telegram_id].umenue = 1


def starte_pc_nach_auswahl(nachricht, bot, users, telegram_id):
    pc = nachricht["message"]["text"].strip("/")
    try:
        mac_addresse = CONFIG["known_computers"][pc]
    except KeyError:
        bot.send_message(telegram_id, f"{pc} nicht bekannt, erneut versuchen oder abbrechen")
    else:
        magic_packet = generate_magic_packet_message(mac_addresse)
        send_magic_packet(CONFIG["broadcast"], CONFIG["wol_port"], magic_packet)
        bot.send_message(telegram_id, f"Magic Packet an {pc} gesendet")
        users[telegram_id].umenue = None
        users[telegram_id].menue = None


def m_starte_pc(nachricht, bot, users, telegram_id):
    users[telegram_id].menue = m_starte_pc
    if users[telegram_id].umenue is None:
        sende_verfuegbare_pcs(nachricht, bot, users, telegram_id)
    elif users[telegram_id].umenue == 1:
        starte_pc_nach_auswahl(nachricht, bot, users, telegram_id)


def m_abbrechen(nachricht, bot, users, telegram_id):
    users[telegram_id].menue = None
    users[telegram_id].umenue = None
    bot.send_message(telegram_id, "Abgebrochen!")


def bot_command(nachricht, bot, users, telegram_id):
    """Hier werden alle Verfügbaren Telegramkommdos angelegt"""
    kommando = nachricht["message"]["text"]
    if kommando == "/starte_pc":
        m_starte_pc(nachricht, bot, users, telegram_id)
    if kommando == "/abbrechen":
        m_abbrechen(nachricht, bot, users, telegram_id)
    elif users[telegram_id].menue is not None:
        users[telegram_id].menue(nachricht, bot, users, telegram_id)


def nachrichten_handler(nachricht, bot, users):
    """Handling der vorliegenden Nachricht"""
    telegram_id = nachricht["message"]["from"]["id"]
    if telegram_id not in users.keys():
        bot.send_message(telegram_id, "Permission denied")
        return
    if "message" in nachricht:
        # Prüfen ob es sich um ein Botkommando handelt
        if "bot_command" in nachricht["message"].get("entities", [{}])[0].get("type", ""):
            bot_command(nachricht, bot, users, telegram_id)
        elif users[telegram_id].menue is not None:
            users[telegram_id].menue(nachricht, bot, users, telegram_id)


def main():
    bot = api.Bot(CONFIG["telegram"]["token"])
    users = {telegramid: User(telegramid) for telegramid in CONFIG["telegram"]["allowed_ids"].values()}
    while True:
        messages = bot.get_updates()
        for message in messages:
            nachrichten_handler(message, bot, users)


if __name__ == "__main__":
    main()
