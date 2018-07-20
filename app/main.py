# -*- coding: utf-8 -*-
import configparser
import json
import locale
import os
import re
import subprocess
import threading
import time
import urllib.request

import strings
import telebot

path = "Settings.ini"

if not os.path.exists(path):
	subprocess.call("python3 config_init.py", shell=True)

config = configparser.ConfigParser()
config.read(path)

bot = telebot.TeleBot(config.get('Settings', 'token'))
msg_id = int(config.get('Settings', 'msg_id'))

addr = config.get('Settings', 'address')
currency = config.get('Settings', 'currency')

stats = 'https://api.nicehash.com/api?method=stats.provider.ex&addr=' + addr
price = 'http://api.coindesk.com/v1/bpi/currentprice/' + currency + '.json'

monitor = False
set_a = False
workers0 = 0
workers1 = 0
k = 0
w = []
price_currency_int, total_workers, profit_btc_day, profit_fiat_day, balance_btc, balance_fiat = 0, 0, 0, 0, 0, 0


def start():
	global price_currency_int
	global total_workers
	global profit_btc_day
	global profit_fiat_day
	global balance_btc
	global balance_fiat
	global w
	w = []
	reqStats = urllib.request.Request(stats)
	threading.Event()
	hdr = {'User-Agent': 'Mozilla/5.0'}
	locale.setlocale(locale.LC_ALL, '')
	reqPrice = urllib.request.Request(price, headers=hdr)
	rPrice = urllib.request.urlopen(reqPrice).read()
	cccc = re.split(currency, str(rPrice))
	ccc = re.split(r'"', cccc[2])
	cc = re.split(r',', ccc[4])
	cc_ = cc[0] + cc[1]
	priceCurrency = float(cc_)
	print("\n\nUsing Currency: BTC/{0} = {1:,.2f}".format(currency, priceCurrency))

	rStats = urllib.request.urlopen(reqStats).read()
	cont = json.loads(rStats.decode('utf-8'))
	counter = 0
	balance = 0
	totalWorkers = 0
	profitability = 0

	try:
		for item in cont['result']['current']:
			counter += 1
			balance += float(item['data'][1])
			print("Algo: ({0}) {1}".format(item['algo'], item['name']))
			worker = 'https://api.nicehash.com/api?method=stats.provider.workers&addr=' + addr + '&algo=' + str(
				item['algo'])
			reqWorkers = urllib.request.Request(worker)
			rWorker = urllib.request.urlopen(reqWorkers).read()
			totalWorkers += len(json.loads(rWorker.decode('utf-8'))['result']['workers'])
			print("Workers: {0}".format(len(json.loads(rWorker.decode('utf-8'))['result']['workers'])))
			if len(item['data'][0]) >= 1:
				w.append(item['name'])
				print("Accepted Speed: {0} {1}/s".format(item['data'][0]['a'], item['suffix']))
				print("Profitability: {0} BTC/day or {1:,.2f} {2}/day".format(
					float(item['profitability']) * float(item['data'][0]['a']),
					float(item['profitability']) * float(item['data'][0]['a']) * priceCurrency, currency))

			if (len(json.loads(rWorker.decode('utf-8'))['result']['workers']) >= 1):
				profitability += float(float(item['profitability']) * float(item['data'][0]['a']))
			print("Balance: {0} BTC or {1:,.2f} {2}".format(item['data'][1], float(item['data'][1]) * priceCurrency,
															currency))
			print("---------------------------------------------------")
	except:
		return ConnectionAbortedError

	price_currency_int = int(priceCurrency)
	#total_algo = counter
	total_workers = totalWorkers
	profit_btc_day = round(profitability, 8)
	profit_fiat_day = round(float(profitability) * priceCurrency, 2)
	balance_btc = round(balance, 8)
	balance_fiat = round(balance * priceCurrency, 2)
	return price_currency_int, w, total_workers, profit_btc_day, profit_fiat_day, balance_btc, balance_fiat


def set_address(address):
	global addr
	global stats
	global set_a
	addr_ = ''
	stats_ = ''
	if address == addr:
		return False
	else:
		config.set('Settings', 'address', address)
		addr_ = addr
		stats_ = stats
		addr = address
		stats = 'https://api.nicehash.com/api?method=stats.provider.ex&addr=' + addr
		if check_address(address):
			with open(path, "w") as config_file:
				config.write(config_file)
			bot.send_message(msg_id, strings.addr_ok)
			set_a = False
		else:
			bot.send_message(msg_id, strings.addr_invalid + ', ' + strings.addr_enter_new)
			set_a = False
			addr = addr_
			stats = stats_


def check_address(address):
	if address == '':
		return False
	try:
		check(0)
		return True
	except:
		return False


def check(kk):
	# Исправить баг с уведомлениями сразу после запуска
	global workers0
	global workers1
	data_ = start()
	if kk % 2 == 0:
		workers0 = int(data_[2])
	if kk % 2 == 1:
		workers1 = int(data_[2])

	if workers0 > workers1:
		bot.send_message(msg_id, strings.worker_stop)
	if workers0 < workers1:
		bot.send_message(msg_id, strings.worker_new)


@bot.message_handler(commands=[strings.start])
def get_data_and_send(message):
	global msg_id
	# Первый пользователь, отправивший команду start боту становится "владельцем"
	# Запросы от других пользователей будут игнорироваться
	if int(config.get("Settings", "msg_id")) == 0:
		msg_id = message.chat.id
		config.set("Settings", "msg_id", str(msg_id))
		with open(path, "w") as config_file:
			config.write(config_file)
		bot.send_message(msg_id, strings.owner_set)
	else:
		if message.chat.id != msg_id:
			bot.send_message(message.chat.id, strings.forbidden)

	if message.chat.id == msg_id:
		bot.send_message(message.chat.id, strings.owner_already)


@bot.message_handler(commands=[strings.get_mining_data])
def get_data_and_send(message):
	if message.chat.id == msg_id:
		try:
			check(1)
			str_send = '1 BTC = ' + str(price_currency_int) + ' ' + currency + '\n\n' + strings.mining_algo + str(
				', '.join(str(v) for v in w) + '\n' + strings.workers_active + str(
					total_workers) + '\n' + strings.profit_per_day + str(profit_btc_day) + ' BTC (' + str(
					profit_fiat_day) + ' ' + currency + ')\n' + strings.unpaid + str(balance_btc) + ' BTC (' + str(
					balance_fiat) + ' ' + currency + ')')
			print(str_send)
			bot.send_message(msg_id, str_send)
		except:
			bot.send_message(msg_id, strings.addr_invalid)


@bot.message_handler(commands=[strings.start_mining_monitoring])
def get_data_and_send(message):
	if message.chat.id == msg_id:
		if check_address(addr):
			try:
				check(1)
				global k
				while True:
					check(k)
					k += 1
					if k == 2:
						k = 0
					time.sleep(30)
			except:
				bot.send_message(msg_id, strings.addr_invalid)


@bot.message_handler(commands=[strings.stop_mining_monitoring])
def get_data_and_send(message):
	if message.chat.id == msg_id:
		global monitor
		monitor = False


@bot.message_handler(commands=[strings.set_address])
def get_data_and_send(message):
	if message.chat.id == msg_id:
		global set_a
		set_a = True
		bot.send_message(msg_id, strings.addr_set)


@bot.message_handler(content_types='text')
def get_data_and_send(message):
	global set_a
	if message.chat.id == msg_id:
		if set_a:
			set_address(message.text)


if __name__ == '__main__':
	try:
		bot.polling(none_stop=True)
	except Exception as e:
		time.sleep(15)
