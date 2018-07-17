# -*- coding: utf-8 -*-
import time
import telebot
import config
import urllib.request
import json
import threading
import locale
import re


bot = telebot.TeleBot(config.token)
msg_id = config.msg_id

addr = '3MLnyrNo3yoAS8a2YdD7AU2638AGZJKbyh'
currency = 'RUB'
stats = 'https://api.nicehash.com/api?method=stats.provider.ex&addr=' + addr
price = 'http://api.coindesk.com/v1/bpi/currentprice/' + currency + '.json'

monitor = False
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


def check(kk):
	global workers0
	global workers1
	data_ = start()
	if kk % 2 == 0:
		workers0 = int(data_[2])
	if kk % 2 == 1:
		workers1 = int(data_[2])

	if workers0 > workers1:
		bot.send_message(msg_id, 'Воркер перестал работать')
	if workers0 < workers1:
		bot.send_message(msg_id, 'Новый воркер')


@bot.message_handler(commands=['data'])
def get_data_and_send(message):
	if message.chat.id == msg_id:
		if price_currency_int == 0:
			check(0)
		str_send = '1 BTC = ' + str(price_currency_int) + ' ' + currency + '\n\n' + 'Алгоритмы майнинга: ' + str(', '.join(str(v) for v in w) + '\n' + 'Активные воркеры: ' + str(total_workers) + '\n' + 'Доход в день: ' + str(profit_btc_day) + ' BTC (' + str(profit_fiat_day) + ' ' + currency + ')\n' + 'Невыплаченный баланс: ' + str(balance_btc) + ' BTC (' + str(balance_fiat) + ' ' + currency + ')')
		print(str_send)
		bot.send_message(msg_id, str_send)


@bot.message_handler(commands=['start'])
def get_data_and_send(message):
	if message.chat.id == msg_id:
		global k
		while True:
			check(k)
			k += 1
			if k == 2:
				k = 0
			time.sleep(30)


@bot.message_handler(commands=['stop'])
def get_data_and_send(message):
	if message.chat.id == msg_id:
		global monitor
		monitor = False


if __name__ == '__main__':
	bot.polling(none_stop=True)
