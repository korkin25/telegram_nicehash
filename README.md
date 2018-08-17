# Telegram bot for monitoring mining (NiceHash)
The project uses the [NiceHash Viewer API](https://github.com/adityudhna/nicehash).

## Features
- Shows the mining profitability, mining algorithms, unpaid balance
- Notification on changes in the number of workers and increase or decrease in profits

## Installing dependencies 
### Ubuntu/Debian
```
apt-get update
apt-get install -y python3 python3-pip
pip3 install -r https://raw.githubusercontent.com/vslvcode/telegram_nicehash/master/requirements.txt
```

## Usage
### First start
Send ```/newbot``` to [@BotFather](https://telegram.me/BotFather) and follow the instructions.
Launch ```main.py```.
```
cd ~
wget https://github.com/vslvcode/telegram_nicehash/archive/master.zip
unzip master.zip
cd telegram_nicehash-master/app
python3 main.py -t bot_token_from_BotFather
```
If you need a proxy to access Telegram, you can use ```-s``` key to enter the SOCKS5 proxy server.
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
cd ~/telegram_nicehash-master/app
python3 main.py
```

### After update

Remove ```settings.ini``` and restart the bot. This action will reset the settings.
```
cd ~/telegram_nicehash-master/app
rm settings.ini
python3 main.py -t bot_token_from_BotFather
```

### Warnings
- Multi-user not supported
- Does not work from Windows

### Demo
![alt text](https://raw.githubusercontent.com/vslvcode/telegram_nicehash/master/demo.png)

## Docker

You can create a Docker image using Dockerfile.
```
cd ~/telegram_nicehash-master
rm app/settings.ini
docker build -t vslvcode/telegram_nicehash .
```
Launch Docker image.

```
docker run vslvcode/telegram_nicehash -t bot_token_from_BotFather

```
