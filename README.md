[RUS]
# Telegram-бот для мониторинга майнинга NiceHash
## Возможности
- Выдача информации о текущем уровне дохода, алгоритмах майнинга и невыплаченном балансе
- Оповещение об изменении количества воркеров

## Установка зависимостей (Debian/Ubuntu)
```
apt-get update
apt-get install -y python3 python3-pip
pip3 install pytelegrambotapi
```
### В config_init.py нужно указать токен бота.
### Многопользовательность не поддерживается.
В проекте использованы фрагменты NiceHash Viewer API
https://github.com/adityudhna/nicehash
