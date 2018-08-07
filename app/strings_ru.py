# -*- coding: utf-8 -*-
import common_str

monitor_start = '⚡️ Мониторинг запущен'
monitor_stop = '✋️ Мониторинг останавливается'
monitor_already_started = 'ℹ️ Мониторинг уже был запущен'
monitor_stops = '❌ Мониторинг ещё останавливается, повторите попытку немного позднее'
monitor_already_stopped = 'ℹ️ Мониторинг не запущен'
monitor_restart = '⚠️ Мониторинг был сброшен.' \
                  '\nНажмите для запуска -> /'\
                  + common_str.start_mining_monitoring
monitor_error = '⚠️ Ошибка получения данных, остановка мониторинга'

cancel = '❌ Закрыть'
cancelled = '❌ Закрыто'
disable_t = '🔕 Отключить порог'

select_curr = '✅ Выберите валюту для отображения'

lang_e = '❌ Этот язык уже выбран'

mining_algo = '💎 Алгоритмы майнинга: '
workers_active = '⛏ Активные воркеры: '
profit_per_day = '💸 Доход в день: '
unpaid = '💰 Невыплаченный баланс: '

forbidden = '❌ Доступ запрещён'

addr_set = '✏️ Введите адрес'
addr_ok = '🆗 Установлено'
addr_invalid = '❌ Невалидный адрес'
addr_enter_new = 'Повторите попытку' + ' /' + common_str.set_address

what_do = '💫 Выберите дальнейшее действие'

keyboard_data = 'ℹ️ Информация'
keyboard_start_monitor = '▶️ Запустить мониторинг'
keyboard_stop_monitor = '⏹ Остановить мониторинг'
keyboard_first_set_address = '🔧 Ввести адрес'
keyboard_set_address = '🔁 Изменить адрес'
keyboard_set_currency = '🔁 Изменить валюту'
keyboard_set_language = '🔁 Изменить язык'
keyboard_set_monitor_n = '🔔 Уведомления мониторинга'

notification_set_menu_msg = '🔔⚙'
notification_true = '🔔 '
notification_false = '🔕 '

set_notification_workers = 'Воркеры'
set_notification_profit_min = '📉'
set_notification_profit_max = '📈'

notification_profit_min_help = '📉 Минимальный порог прибыли\nУкажите в'
notification_profit_max_help = '📉 Максимальный порог прибыли\nУкажите в'
notification_profit_error = '⚠️ Нужно ввести только целое или дробное число'
notification_profit_ok = '🆗 Записано'
notification_profit_min_alert = '📉 Прибыль опустилась ниже порога'
notification_profit_min_no = '📈 Прибыль вернулась за порог минимума'
notification_profit_max_alert = '📈 Прибыль поднялась выше верхнего порога'
notification_profit_max_no = '📉 Прибыль вернулась за порог максимума'

notification_pr_err = '⚠️ Нижний порог больше верхнего. Вы уверены?'
notification_pr_err_ok = '🤷‍♀️ Сохранить'
notification_pr_err_return = '⤴️ Повторить'
notification_pr_err_dis_min = '🔕 min и сохранить'
notification_pr_err_dis_max = '🔕 max и сохранить'


notification_workers_disabled = '🔕 Оповещения об изменении числа воркеров отключены'
notification_workers_enabled = '🔔 Оповещения об изменении числа воркеров включены'
notification_profit_min_disabled = '🔕 Оповещение минимального порога прибыли выключено'
notification_profit_max_disabled = '🔕 Оповещение максимального порога прибыли выключено'
