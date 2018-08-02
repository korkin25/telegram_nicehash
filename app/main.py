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
import argparse

import common_str
import telebot
from telebot import types

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--token', action='store', dest='t', help='token')
rr = parser.parse_args()

path = "settings.ini"

if not os.path.exists(path):
	subprocess.call("python3 config_init.py", shell=True)

config = configparser.ConfigParser()
config.read(path)

def save_config():
	global config_file
	with open(path, "w") as config_file:
		config.write(config_file)

if rr.t is not None:
	bot = telebot.TeleBot(rr.t)
	config.set('settings', 'token', rr.t)
	save_config()
else:
	if config.get('settings', 'token') != '':
		bot = telebot.TeleBot(config.get('settings', 'token'))
	else:
		print(common_str.token_help)

msg_id = int(config.get('settings', 'msg_id'))

lang = config.get('settings', 'language')
addr = config.get('settings', 'address')
curr = config.get('settings', 'currency')
interval = int(config.get('settings', 'interval_s'))

if lang == 'ru':
	import strings_ru as strings
if lang == 'en':
	import strings_en as strings

stats = 'https://api.nicehash.com/api?method=stats.provider.ex&addr=' + addr
price = 'http://api.coindesk.com/v1/bpi/currentprice/' + curr + '.json'

monitor = False
loop_term = True
lang_lock = False
m_fail = False
set_a = False
workers0 = 0
workers1 = 0
ch_notify = False
k = 0
w = []
price_currency_int, total_workers, profit_btc_day, profit_fiat_day, balance_btc, balance_fiat = 0, 0, 0, 0, 0, 0
lang_sel = False

keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)


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
	cccc = re.split(curr, str(rPrice))
	if curr == 'USD':
		cccc_i = -1
		ccc_i = -1
	else:
		cccc_i = 2
		ccc_i = 4
	ccc = re.split(r'"', cccc[cccc_i])
	cc = re.split(r',', ccc[ccc_i])
	if curr == 'USD':
		cc_ = cc[0][1:-4]
	else:
		cc_ = cc[0] + cc[1]
	priceCurrency = float(cc_)
	print("\n\nUsing Currency: BTC/{0} = {1:,.2f}".format(curr, priceCurrency))

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
					float(item['profitability']) * float(item['data'][0]['a']) * priceCurrency, curr))

			if (len(json.loads(rWorker.decode('utf-8'))['result']['workers']) >= 1):
				profitability += float(float(item['profitability']) * float(item['data'][0]['a']))
			print("Balance: {0} BTC or {1:,.2f} {2}".format(item['data'][1], float(item['data'][1]) * priceCurrency,
															curr))
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
	if address == addr:
		return False
	else:
		config.set('settings', 'address', address)
		addr_ = addr
		stats_ = stats
		addr = address
		stats = 'https://api.nicehash.com/api?method=stats.provider.ex&addr=' + addr
		if check_address(address):
			save_config()
			set_keyboard(1, 2)
			bot.send_message(msg_id, strings.addr_ok, reply_markup=keyboard)
			set_a = False
		else:
			bot.send_message(msg_id, strings.addr_invalid + '\n' + strings.addr_enter_new)
			set_a = False
			addr = addr_
			stats = stats_


def set_language(language):
	global lang

	lang = language
	config.set('settings', 'language', language)
	save_config()


def set_currency(currency):
	global curr
	global price

	curr = currency
	price = 'http://api.coindesk.com/v1/bpi/currentprice/' + curr + '.json'
	config.set('settings', 'currency', curr)
	save_config()


def check_address(address):
	if address == '':
		return False
	try:
		check(3)
		return True
	except:
		return False


def check(kk):
	global workers0
	global workers1
	global total_workers
	global ch_notify
	data_ = start()
	if kk != 3:
		if kk % 2 == 0:
			workers0 = int(data_[2])
		if kk % 2 == 1:
			workers1 = int(data_[2])
		ch_notify += 1
		if ch_notify > 2:
			ch_notify = 2  # Чтобы лишний раз не расходовать память
		if ch_notify >= 2:
			if workers0 != workers1:
				bot.send_message(msg_id, strings.workers_active + str(total_workers))
	else:
		int(data_[2])


def set_keyboard(arg, rw):
	global keyboard
	keyboard = types.ReplyKeyboardMarkup(row_width=rw, resize_keyboard=True)
	kb_data = types.KeyboardButton(text=strings.keyboard_data)
	kb_start_m = types.KeyboardButton(text=strings.keyboard_start_monitor)
	kb_stop_m = types.KeyboardButton(text=strings.keyboard_stop_monitor)
	kb_f_set_a = types.KeyboardButton(text=strings.keyboard_first_set_address)
	kb_set_a = types.KeyboardButton(text=strings.keyboard_set_address)
	kb_set_c = types.KeyboardButton(text=strings.keyboard_set_currency)
	kb_set_l = types.KeyboardButton(text=strings.keyboard_set_language)
	if arg == 0:
		keyboard.add(kb_f_set_a, kb_set_c)
	if arg == 1:
		keyboard.add(kb_start_m, kb_stop_m, kb_data, kb_set_a, kb_set_c, kb_set_l)


@bot.message_handler(commands=[common_str.start])
def a(message):
	global msg_id
	# Первый пользователь, отправивший команду start боту становится "владельцем"
	# Запросы от других пользователей будут игнорироваться
	if int(config.get("settings", "msg_id")) == 0:
		msg_id = message.chat.id
		config.set("settings", "msg_id", str(msg_id))
		save_config()
		if lang == '':
			_set_language(message)
	else:
		if message.chat.id != msg_id:
			bot.send_message(message.chat.id, strings.forbidden)
		if message.chat.id == msg_id:
			if addr == '':
				set_keyboard(0, 1)
			else:
				set_keyboard(1, 2)
			bot.send_message(msg_id, strings.what_do, reply_markup=keyboard)


def _get_mining_data(message):
	if message.chat.id == msg_id:
		set_keyboard(1, 2)
		try:
			check(3)
			str_send = '1 BTC = ' + str(price_currency_int) + ' ' + curr + '\n\n' + strings.mining_algo + str(
				', '.join(str(v) for v in w) + '\n' + strings.workers_active + str(
					total_workers) + '\n' + strings.profit_per_day + str(profit_btc_day) + ' BTC (' + str(
					profit_fiat_day) + ' ' + curr + ')\n' + strings.unpaid + str(balance_btc) + ' BTC (' + str(
					balance_fiat) + ' ' + curr + ')')
			print(str_send)
			bot.send_message(msg_id, str_send, reply_markup=keyboard)
		except:
			set_keyboard(0, 1)
			bot.send_message(msg_id, strings.addr_invalid, reply_markup=keyboard)


@bot.message_handler(commands=[common_str.get_mining_data])
def a(message):
	_get_mining_data(message)


def _start_mining_monitoring(message):
	if message.chat.id == msg_id:
		set_keyboard(1, 2)
		global monitor
		global loop_term
		if not monitor:
			if loop_term:
				monitor = True
				bot.send_message(msg_id, strings.monitor_start)
				if check_address(addr):
					config.set('settings', 'monitor', '1')
					save_config()
					global k
					try:
						while monitor:
							loop_term = False
							check(k)
							k += 1
							if k == 2:
								k = 0
							time.sleep(interval)
							loop_term = True
					except:
						set_keyboard(0, 1)
						bot.send_message(msg_id, strings.addr_invalid)
						monitor = False
						loop_term = True
			else:
				bot.send_message(msg_id, strings.monitor_stops, reply_markup=keyboard)
		else:
			bot.send_message(msg_id, strings.monitor_already_started, reply_markup=keyboard)


@bot.message_handler(commands=[common_str.start_mining_monitoring])
def a(message):
	_start_mining_monitoring(message)


def _stop_mining_monitoring(message):
	if message.chat.id == msg_id:
		global monitor
		if monitor:
			monitor = False
			bot.send_message(msg_id, strings.monitor_stop)
			config.set('settings', 'monitor', '0')
			save_config()
		else:
			bot.send_message(msg_id, strings.monitor_already_stopped)


@bot.message_handler(commands=[common_str.stop_mining_monitoring])
def a(message):
	_stop_mining_monitoring(message)


def _set_address(message):
	if message.chat.id == msg_id:
		global set_a
		set_a = True
		bot.send_message(msg_id, strings.addr_set)


@bot.message_handler(commands=[common_str.set_address])
def a(message):
	_set_address(message)


def _0set_language():
	keyboard = types.InlineKeyboardMarkup()
	button_ru = types.InlineKeyboardButton(text=common_str.ru, callback_data='ru')
	button_en = types.InlineKeyboardButton(text=common_str.en, callback_data='en')
	keyboard.add(button_ru, button_en)
	bot.send_message(msg_id, common_str.select_lang, reply_markup=keyboard)


def _set_language(message):
	if message.chat.id == msg_id:
		global lang_sel
		global monitor
		global lang_lock
		global m_fail
		if not lang_lock:
			lang_lock = True
			monitor = False
			_0set_language()
			lt = lang
			while not lang_sel:
				if monitor:
					m_fail = True
					break
			lang_sel = False
			lang_lock = False
			if lt != lang:
				bot.send_message(msg_id, common_str.restarting)
				subprocess.call('chmod +x restart.sh', shell=True)
				subprocess.Popen('./restart.sh', shell=True)
			else:
				if not m_fail:
					bot.send_message(msg_id, strings.lang_e)
					bot.send_message(msg_id, strings.monitor_restart)
					config.set('settings', 'monitor', '0')
					save_config()

@bot.message_handler(commands=[common_str.set_language])
def a(message):
	_set_language(message)


def _set_currency(message):
	if message.chat.id == msg_id:
		keyboard = types.InlineKeyboardMarkup()
		button_usd = types.InlineKeyboardButton(text=common_str.USD, callback_data='USD')
		button_rub = types.InlineKeyboardButton(text=common_str.RUB, callback_data='RUB')
		button_uah = types.InlineKeyboardButton(text=common_str.UAH, callback_data='UAH')
		keyboard.add(button_usd, button_rub, button_uah)
		bot.send_message(msg_id, strings.select_curr, reply_markup=keyboard)


@bot.message_handler(commands=[common_str.set_currency])
def a(message):
	_set_currency(message)


@bot.callback_query_handler(func=lambda call: True)
def a(call):
	global lang_sel
	global m_fail
	if call.message:
		if call.data == 'USD':
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=common_str.USD)
			set_currency(call.data)
		if call.data == 'RUB':
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=common_str.RUB)
			set_currency(call.data)
		if call.data == 'UAH':
			set_currency(call.data)
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=common_str.UAH)

		if call.data == 'ru':
			if m_fail:
				bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
				m_fail = False
			else:
				bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
									  text=common_str.ru)
				lang_sel = True
				set_language(call.data)
		if call.data == 'en':
			if m_fail:
				bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
				m_fail = False
			else:
				bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
									  text=common_str.en)
				lang_sel = True
				set_language(call.data)

@bot.message_handler(content_types='text')
def a(message):
	global set_a
	if message.chat.id == msg_id:
		if message.text == strings.keyboard_data:
			_get_mining_data(message)
		if message.text == strings.keyboard_start_monitor:
			_start_mining_monitoring(message)
		if message.text == strings.keyboard_stop_monitor:
			_stop_mining_monitoring(message)
		if message.text == strings.keyboard_set_address or message.text == strings.keyboard_first_set_address:
			_set_address(message)
		if message.text == strings.keyboard_set_currency:
			_set_currency(message)
		if message.text == strings.keyboard_set_language:
			_set_language(message)

		if set_a:
			if message.text != strings.keyboard_data and message.text != strings.keyboard_start_monitor \
					and message.text != strings.keyboard_stop_monitor\
					and message.text != strings.keyboard_set_address \
					and message.text != strings.keyboard_first_set_address\
					and message.text != strings.keyboard_set_currency\
					and message.text != strings.keyboard_set_language:
				set_address(message.text)


if lang != '' and msg_id != 0:
	if addr == '':
		set_keyboard(0, 1)
		bot.send_message(msg_id, strings.what_do, reply_markup=keyboard)
	else:
		set_keyboard(1, 2)
		if config.get('settings', 'monitor') == '1':
			bot.send_message(msg_id, strings.monitor_restart, reply_markup=keyboard)
			config.set('settings', 'monitor', '0')
			save_config()
		else:
			bot.send_message(msg_id, strings.what_do, reply_markup=keyboard)


if __name__ == '__main__':
	try:
		bot.polling(none_stop=True)
	except Exception as e:
		time.sleep(15)
