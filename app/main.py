# -*- coding: utf-8 -*-
import argparse
import configparser
import json
import locale
import os
import re
import subprocess
import threading
import time
import urllib.request

import common_str
import telebot
from currency_converter import CurrencyConverter
from telebot import types

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--socks', action='store', dest='s', help='SOCKS5 proxy')
parser.add_argument('-t', '--token', action='store', dest='t', help='token')
rr = parser.parse_args()

path = "settings.ini"

if not os.path.exists(path):
	subprocess.call("python3 config_init.py", shell=True)

config = configparser.ConfigParser()
config.read(path)


def save_config():
	with open(path, "w") as config_file:
		config.write(config_file)


if rr.s is not None:
	if rr.s == '0':
		config.set('settings', 'socks5', '')
		save_config()
	else:
		config.set('settings', 'socks5', rr.s)
		save_config()

if config.get('settings', 'socks5') != '':
	socks5_s = config.get('settings', 'socks5')
	socks5_l = re.split(r':', socks5_s)
	import socks
	import socket
	socks.set_default_proxy(socks.SOCKS5, socks5_l[0], int(socks5_l[1]))
	socket.socket = socks.socksocket

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
min_profit_n = float(config.get('settings', 'min_profit_n'))
max_profit_n = float(config.get('settings', 'max_profit_n'))

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
set_pr_min = False
set_pr_max = False
btn_min_t_dis = False
btn_max_t_dis = False
p_min_notification = False
p_max_notification = False
workers0 = 0
workers1 = 0
ch_notify = False
profit_list = []
profit_l_first = True
curr_changed = False
profit_avg_f = 0.0
profit_avg_num = 0
k = 0
w = []
price_currency_int, total_workers, profit_btc_day, profit_fiat_day, balance_btc, balance_fiat = 0, 0, 0, 0, 0, 0
lang_sel = False

keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

if config.get('settings', 'workers_n') == '1':
	worker_notification = True
else:
	worker_notification = False


def start():
	global price_currency_int
	global total_workers
	global profit_btc_day
	global profit_fiat_day
	global balance_btc
	global balance_fiat
	global w
	w = []
	req_stats = urllib.request.Request(stats)
	threading.Event()
	hdr = {'User-Agent': 'Mozilla/5.0'}
	locale.setlocale(locale.LC_ALL, '')
	req_price = urllib.request.Request(price, headers=hdr)
	r_price = urllib.request.urlopen(req_price).read()
	cccc = re.split(curr, str(r_price))
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
	price_currency = float(cc_)

	r_stats = urllib.request.urlopen(req_stats).read()
	cont = json.loads(r_stats.decode('utf-8'))
	counter = 0
	balance = 0
	total_workers_ = 0
	profitability = 0

	try:
		for item in cont['result']['current']:
			counter += 1
			balance += float(item['data'][1])
			worker = 'https://api.nicehash.com/api?method=stats.provider.workers&addr=' + addr + '&algo=' + str(
				item['algo'])
			req_workers = urllib.request.Request(worker)
			r_worker = urllib.request.urlopen(req_workers).read()
			total_workers_ += len(json.loads(r_worker.decode('utf-8'))['result']['workers'])
			if len(item['data'][0]) >= 1:
				w.append(item['name'])

			if len(json.loads(r_worker.decode('utf-8'))['result']['workers']) >= 1:
				profitability += float(float(item['profitability']) * float(item['data'][0]['a']))
	except:
		return ConnectionAbortedError

	price_currency_int = int(price_currency)
	total_workers = total_workers_
	profit_btc_day = round(profitability, 8)
	profit_fiat_day = round(float(profitability) * price_currency, 2)
	balance_btc = round(balance, 8)
	balance_fiat = round(balance * price_currency, 2)
	return price_currency_int, w, total_workers, profit_btc_day, profit_fiat_day, balance_btc, balance_fiat


def set_address(address):
	global addr
	global stats
	global set_a
	global profit_list
	global profit_l_first
	if address == addr:
		return False
	else:
		addr_ = addr
		stats_ = stats
		addr = address
		stats = 'https://api.nicehash.com/api?method=stats.provider.ex&addr=' + addr
		if check_address(address):
			config.set('settings', 'address', address)
			save_config()
			profit_list = []
			profit_l_first = True
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
	global curr_changed
	curr_old = config.get('settings', 'currency')
	if curr_old != currency:
		curr = currency
		price = 'http://api.coindesk.com/v1/bpi/currentprice/' + curr + '.json'
		config.set('settings', 'currency', curr)
		save_config()
		curr_changed = True


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
	global profit_list
	global profit_l_first
	global profit_avg_f
	global profit_avg_num
	global p_min_notification
	global p_max_notification
	global curr_changed
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
			if workers0 != workers1 and worker_notification:
				bot.send_message(msg_id, strings.workers_active + str(total_workers))

		len_list_p = 10
		if curr_changed:
			profit_list = []
			profit_l_first = True
			curr_changed = False
		if profit_l_first and len(profit_list) < len_list_p:
			profit_list.append(data_[4])
			profit_avg_f = sum(profit_list)/len(profit_list)
		if len(profit_list) == len_list_p:
			profit_avg_f = sum(profit_list)/len(profit_list)
			profit_list[profit_avg_num] = data_[4]
			profit_avg_num += 1
			if profit_avg_num == len_list_p:
				profit_avg_num = 0
			profit_l_first = False

		if profit_avg_f < min_profit_n != 0.0 and not p_min_notification:
			bot.send_message(msg_id, strings.notification_profit_min_alert + '\n' + strings.profit_per_day + str(
				profit_avg_f) + ' ' + curr)
			p_min_notification = True
		if profit_avg_f > min_profit_n != 0.0 and p_min_notification:
			bot.send_message(msg_id, strings.notification_profit_min_no + '\n' + strings.profit_per_day + str(
				profit_avg_f) + ' ' + curr)
			p_min_notification = False
		if profit_avg_f > max_profit_n != 0.0 and not p_max_notification:
			bot.send_message(msg_id, strings.notification_profit_max_alert + '\n' + strings.profit_per_day + str(
				profit_avg_f) + ' ' + curr)
			p_max_notification = True
		if profit_avg_f < max_profit_n != 0.0 and p_max_notification:
			bot.send_message(msg_id, strings.notification_profit_max_no + '\n' + strings.profit_per_day + str(
				profit_avg_f) + ' ' + curr)
			p_max_notification = False
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
	kb_set_m_n = types.KeyboardButton(text=strings.keyboard_set_monitor_n)
	if arg == 0:
		keyboard.add(kb_f_set_a, kb_set_c)
	if arg == 1:
		keyboard.add(kb_start_m, kb_stop_m, kb_set_m_n, kb_set_a, kb_set_c, kb_set_l, kb_data)


def check_pr_err_():
	if (min_profit_n and max_profit_n) != 0.0:
		if min_profit_n < max_profit_n:
			return True
		else:
			return False
	else:
		return True


def inline_kb_set_pr(arg):
	keyboard = types.InlineKeyboardMarkup()

	if arg == 0:
		button_pr_err_ok = types.InlineKeyboardButton(text=strings.notification_pr_err_ok,
													  callback_data='pr_err_ok_min')
		button_pr_err_return = types.InlineKeyboardButton(text=strings.notification_pr_err_return,
														  callback_data='pr_err_return_min')
		button_pr_err_disable_max = types.InlineKeyboardButton(text=strings.notification_pr_err_dis_max,
															   callback_data='pr_err_dis_max')
		keyboard.add(button_pr_err_ok, button_pr_err_return, button_pr_err_disable_max)
		bot.send_message(msg_id, strings.notification_pr_err, reply_markup=keyboard)
	if arg == 1:
		button_pr_err_ok = types.InlineKeyboardButton(text=strings.notification_pr_err_ok,
													  callback_data='pr_err_ok_max')
		button_pr_err_return = types.InlineKeyboardButton(text=strings.notification_pr_err_return,
														  callback_data='pr_err_return_max')
		button_pr_err_disable_min = types.InlineKeyboardButton(text=strings.notification_pr_err_dis_min,
															   callback_data='pr_err_dis_min')
		keyboard.add(button_pr_err_ok, button_pr_err_return, button_pr_err_disable_min)
		bot.send_message(msg_id, strings.notification_pr_err, reply_markup=keyboard)

	if arg == 2:
		button_pr_err_return = types.InlineKeyboardButton(text=strings.notification_pr_err_return,
														  callback_data='pr_err_return_min')
		button_pr_cancel = types.InlineKeyboardButton(text=strings.cancel,
															   callback_data='cancel')
		keyboard.add(button_pr_err_return, button_pr_cancel)
		bot.send_message(msg_id, strings.notification_profit_error, reply_markup=keyboard)
	if arg == 3:
		button_pr_err_return = types.InlineKeyboardButton(text=strings.notification_pr_err_return,
														  callback_data='pr_err_return_max')
		button_pr_cancel = types.InlineKeyboardButton(text=strings.cancel,
													  callback_data='cancel')
		keyboard.add(button_pr_err_return, button_pr_cancel)
		bot.send_message(msg_id, strings.notification_profit_error, reply_markup=keyboard)


def set_pr_min_(pr_min):
	global set_pr_min
	global min_profit_n
	global p_min_notification
	set_pr_min = False
	p_min_notification = False
	try:
		min_profit_n = float(pr_min)
		if check_pr_err_():
			config.set('settings', 'min_profit_n', pr_min)
			save_config()
			if min_profit_n == 0.0:
				bot.send_message(msg_id, strings.notification_profit_min_disabled)
			else:
				bot.send_message(msg_id, strings.notification_profit_ok)
		else:
			inline_kb_set_pr(0)
	except:
		inline_kb_set_pr(2)


def set_pr_max_(pr_max):
	global set_pr_max
	global max_profit_n
	global p_max_notification
	set_pr_max = False
	p_max_notification = False
	try:
		max_profit_n = float(pr_max)
		if check_pr_err_():
			config.set('settings', 'max_profit_n', pr_max)
			save_config()
			if max_profit_n == 0.0:
				bot.send_message(msg_id, strings.notification_profit_max_disabled)
			else:
				bot.send_message(msg_id, strings.notification_profit_ok)
		else:
			inline_kb_set_pr(1)
	except:
		inline_kb_set_pr(3)


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
		except:
			bot.send_message(msg_id, strings.url_error, reply_markup=keyboard)

		str_send = '1 BTC = ' + str(price_currency_int) + ' ' + curr + '\n\n' + strings.mining_algo + str(
			', '.join(str(v) for v in w) + '\n' + strings.workers_active + str(
				total_workers) + '\n' + strings.profit_per_day + str(profit_btc_day) + ' BTC (' + str(
				profit_fiat_day) + ' ' + curr + ')\n' + strings.unpaid + str(balance_btc) + ' BTC (' + str(
				balance_fiat) + ' ' + curr + ')')
		str_send = str_send.encode('utf-8')
		bot.send_message(msg_id, str_send, reply_markup=keyboard)


@bot.message_handler(commands=[common_str.get_mining_data])
def a(message):
	_get_mining_data(message)


def _start_mining_monitoring(message):
	if message.chat.id == msg_id:
		set_keyboard(1, 2)
		global monitor
		global loop_term
		global profit_list
		global profit_l_first
		if not monitor:
			if loop_term:
				monitor = True
				profit_list = []
				profit_l_first = True
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
						pass
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
		keyboard = types.InlineKeyboardMarkup()
		button_cancel_sa = types.InlineKeyboardButton(text=strings.cancel, callback_data='cancel_sa')
		keyboard.add(button_cancel_sa)
		bot.send_message(msg_id, strings.addr_set, reply_markup=keyboard)


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
			ms_b = monitor
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
					if ms_b:
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
		button_cancel_c = types.InlineKeyboardButton(text=strings.cancel, callback_data='cancel')
		keyboard.add(button_usd, button_rub, button_cancel_c)
		bot.send_message(msg_id, strings.select_curr, reply_markup=keyboard)


@bot.message_handler(commands=[common_str.set_currency])
def a(message):
	_set_currency(message)


def _set_notifications(message):
	if message.chat.id == msg_id:
		global btn_min_t_dis
		global btn_max_t_dis
		keyboard = types.InlineKeyboardMarkup()
		workers_n_ = config.get('settings', 'workers_n')

		if workers_n_ == '1':
			workers_n_callback = 'wo_0'
			btn_workers_n_label = strings.notification_false
		else:
			workers_n_callback = 'wo_1'
			btn_workers_n_label = strings.notification_true

		if float(config.get('settings', 'min_profit_n')) == 0.0:
			btn_min_p_n_label = strings.notification_true + strings.set_notification_profit_min
			btn_min_t_dis = False
		else:
			btn_min_p_n_label = strings.notification_false + strings.notification_true + strings.set_notification_profit_min
			btn_min_p_n_label += str(int(float(config.get('settings', 'min_profit_n'))))
			btn_min_t_dis = True
		min_p_callback = 'pr_min'

		if float(config.get('settings', 'max_profit_n')) == 0.0:
			btn_max_p_n_label = strings.notification_true + strings.set_notification_profit_max
			btn_max_t_dis = False
		else:
			btn_max_p_n_label = strings.notification_false + strings.notification_true + strings.set_notification_profit_max
			btn_max_p_n_label += str(int(float(config.get('settings', 'max_profit_n'))))
			btn_max_t_dis = True
		max_p_callback = 'pr_max'

		btn_workers_n_label += strings.set_notification_workers

		button_workers_n = types.InlineKeyboardButton(text=btn_workers_n_label, callback_data=workers_n_callback)
		button_min_p_n = types.InlineKeyboardButton(text=btn_min_p_n_label, callback_data=min_p_callback)
		button_max_p_n = types.InlineKeyboardButton(text=btn_max_p_n_label, callback_data=max_p_callback)
		button_cancel_n = types.InlineKeyboardButton(text=strings.cancel, callback_data='cancel')
		keyboard.add(button_workers_n, button_min_p_n, button_max_p_n, button_cancel_n)
		bot.send_message(msg_id, strings.notification_set_menu_msg, reply_markup=keyboard)


@bot.message_handler(commands=[common_str.set_notifications])
def a(message):
	_set_notifications(message)


@bot.callback_query_handler(func=lambda call: True)
def a(call):
	global lang_sel
	global m_fail
	global worker_notification
	global set_pr_min
	global set_pr_max
	if call.message:
		if call.data == 'cancel':
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
								  text=strings.cancelled)

		if call.data == 'cancel_sa':
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
								  text=strings.cancelled)
			global set_a
			set_a = False
		if call.data == 'cancel_pr_min':
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
								  text=strings.cancelled)
			set_pr_min = False
		if call.data == 'cancel_pr_max':
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
								  text=strings.cancelled)
			set_pr_max = False

		def convert_t_curr_and_set(currency):
			global min_profit_n
			global max_profit_n
			if min_profit_n != 0.0:
				c = CurrencyConverter()
				min_profit_n = c.convert(min_profit_n, curr, currency)
				config.set('settings', 'min_profit_n', str(min_profit_n))
				save_config()
			if max_profit_n != 0.0:
				c = CurrencyConverter()
				max_profit_n = c.convert(max_profit_n, curr, currency)
				config.set('settings', 'max_profit_n', str(max_profit_n))
				save_config()
			set_currency(currency)

		if call.data == 'USD':
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=common_str.USD)
			convert_t_curr_and_set(call.data)
		if call.data == 'RUB':
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=common_str.RUB)
			convert_t_curr_and_set(call.data)

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

		if call.data == 'wo_0':
			config.set('settings', 'workers_n', '0')
			save_config()
			worker_notification = False
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
								  text=strings.notification_workers_disabled)
		if call.data == 'wo_1':
			config.set('settings', 'workers_n', '1')
			save_config()
			worker_notification = True
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
								  text=strings.notification_workers_enabled)

		if call.data == 'pr_min':
			set_pr_min = True
			keyboard = types.InlineKeyboardMarkup()
			button_disable_m_p = types.InlineKeyboardButton(text=strings.disable_t, callback_data='disable_min')
			button_cancel_min_t = types.InlineKeyboardButton(text=strings.cancel, callback_data='cancel_pr_min')
			if btn_min_t_dis:
				keyboard.add(button_disable_m_p, button_cancel_min_t)
			else:
				keyboard.add(button_cancel_min_t)
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
								  text=strings.notification_profit_min_help + ' ' + curr, reply_markup=keyboard)
		if call.data == 'disable_min':
			set_pr_min_('0')
			bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

		if call.data == 'pr_max':
			set_pr_max = True
			keyboard = types.InlineKeyboardMarkup()
			button_disable_m_p = types.InlineKeyboardButton(text=strings.disable_t, callback_data='disable_max')
			button_cancel_max_t = types.InlineKeyboardButton(text=strings.cancel, callback_data='cancel_pr_max')
			if btn_max_t_dis:
				keyboard.add(button_disable_m_p, button_cancel_max_t)
			else:
				keyboard.add(button_cancel_max_t)
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
								  text=strings.notification_profit_max_help + ' ' + curr, reply_markup=keyboard)
		if call.data == 'disable_max':
			set_pr_max_('0')
			bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

		def save_pr_after_err(arg):
			if arg == 0:
				config.set('settings', 'min_profit_n', str(min_profit_n))
			if arg == 1:
				config.set('settings', 'max_profit_n', str(max_profit_n))

			save_config()
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
								  text=strings.notification_profit_ok)

		if call.data == 'pr_err_ok_min':
			save_pr_after_err(0)

		if call.data == 'pr_err_ok_max':
			save_pr_after_err(1)

		if call.data == 'pr_err_return_min':
			set_pr_min = True
			keyboard = types.InlineKeyboardMarkup()
			button_cancel_min_t = types.InlineKeyboardButton(text=strings.cancel, callback_data='cancel_pr_min')
			keyboard.add(button_cancel_min_t)
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
								  text=strings.notification_profit_min_help + ' ' + curr, reply_markup=keyboard)
		if call.data == 'pr_err_return_max':
			set_pr_max = True
			keyboard = types.InlineKeyboardMarkup()
			button_cancel_min_t = types.InlineKeyboardButton(text=strings.cancel, callback_data='cancel_pr_max')
			keyboard.add(button_cancel_min_t)
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
								  text=strings.notification_profit_max_help + ' ' + curr, reply_markup=keyboard)
		if call.data == 'pr_err_dis_max':
			set_pr_max_('0')
			save_pr_after_err(0)

		if call.data == 'pr_err_dis_min':
			set_pr_min_('0')
			save_pr_after_err(1)


@bot.message_handler(content_types='text')
def a(message):
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
		if message.text == strings.keyboard_set_monitor_n:
			_set_notifications(message)

		if set_a or set_pr_min or set_pr_max:
			if message.text != strings.keyboard_data \
					and message.text != strings.keyboard_start_monitor \
					and message.text != strings.keyboard_stop_monitor \
					and message.text != strings.keyboard_set_address \
					and message.text != strings.keyboard_first_set_address \
					and message.text != strings.keyboard_set_currency \
					and message.text != strings.keyboard_set_language \
					and message.text != strings.keyboard_set_monitor_n:
				if set_a:
					set_address(message.text)
				if set_pr_min:
					set_pr_min_(message.text)
				if set_pr_max:
					set_pr_max_(message.text)


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
