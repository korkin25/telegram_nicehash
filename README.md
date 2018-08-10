# Telegram bot for monitoring mining (NiceHash)
The project uses the [NiceHash Viewer API](https://github.com/adityudhna/nicehash)

## Features
- Shows the mining profitability, mining algorithms, unpaid balance
- Notification on changes in the number of workers and increase or decrease in profits

## Installing dependencies 
### Ubuntu/Debian
```
apt-get update
apt-get install -y python3 python3-pip
pip3 install pytelegrambotapi
pip3 install currencyconverter
pip3 install requests[socks]
```

## Usage
### First start
Send ```/newbot``` to [@BotFather](https://telegram.me/BotFather) and follow the instructions.
Launch ```main.py```.
```
cd /path_to_bot/app
python3 main.py -t bot_token_from_BotFather
```
If you need a proxy to access the Internet, you can use ```-s``` key to enter the SOCKS5 proxy server.
```
python3 main.py -s x.x.x.x:x
```
To disable the proxy, stop the bot and use ```-s 0```.
```
pkill -f main.py
python3 main.py -s 0
```
Send ```/start``` to your bot and follow the instructions.

You can start the bot the next time without entering a token or proxy.
```
cd /path_to_bot/app
python3 main.py
```

### After update

Remove ```settings.ini``` and restart the bot. This action will reset the settings.
```
cd /path_to_bot/app
rm settings.ini
python3 main.py -t bot_token_from_BotFather
```

### Warnings
- Multi-user not supported
- Does not work from Windows
