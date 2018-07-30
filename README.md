# Telegram bot for monitoring mining (NiceHash)
The project uses the NiceHash Viewer API snippets
https://github.com/adityudhna/nicehash

## Features
- Shows the mining profitability, mining algorithms, unpaid balance
- Notification when changing the number of workers

## Installing dependencies (Debian/Ubuntu)
```
apt-get update
apt-get install -y python3 python3-pip
pip3 install pytelegrambotapi
```

## Usage
###First start
Send ```/newbot``` to [@BotFather](https://telegram.me/BotFather) and follow the instructions.
Write your bot token in ```config_init.py```.
For example:
```
token = '1233424243:GfvdhvT2DgVtnwzefgugGUgjjElFR4Ukbu'
```
Launch ```main.py```
```
cd /path_to_bot/app
python3 main.py
```
Send ```/start``` to your bot and follow the instructions.

![Alt Text](http://ipic.su/img/img7/fs/doc_2018-07-30_16-46-07.1532945054.gif)
###After update

Remove ```Settings.ini``` and restart bot. This action will reset the settings.
```
cd /path_to_bot/app
rm Settings.ini
./restart.sh
```

###Warnings
- Multi-user not supported
- Does not work from Windows
