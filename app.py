#!/usr/bin/env python3

from subprocess import check_output
from time import sleep

from meh import Config, Option, ExceptionInConfigError
import telegram

CONFIG_PATH = "config.cfg"

def process_netstat(decoded_netstat_output):
	tcp_peers = []

	for connection in decoded_netstat_output.split("\n"):
		if connection.startswith("tcp"):
			tcp_peers.append(connection.split()[3])

	return tcp_peers


config = Config()
config += Option("telegram_secret", None)
config += Option("group_id", None)
config += Option("peer", "0.0.0.0:8082")

try:
	config = config.load(CONFIG_PATH)
except (IOError, ExceptionInConfigError):
	config.dump(CONFIG_PATH)
	config = config.load(CONFIG_PATH)

bot = telegram.Bot(config.telegram_secret)

was_offline = False
is_offline = False

while 1:
	tcp_peers = process_netstat(check_output(["netstat", "-tuln"]).decode())
	is_offline = config.peer not in tcp_peers

	if not was_offline and is_offline:
		bot.send_message(
			text="went down pls fix (einfach aus/einstecken sollte reichen)",
			chat_id=config.group_id)
		was_offline = True
	elif was_offline and not is_offline:
		bot.send_message(text="back up, cool", chat_id=config.group_id)
		was_offline = False

	sleep(10)