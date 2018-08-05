# -*- coding: utf-8 -*-
import common_str

monitor_start = '⚡️ Monitoring started'
monitor_stop = '✋️ Monitoring stops...'
monitor_already_started = 'ℹ️ Monitoring already started'
monitor_stops = '❌ Monitoring stops... Try again later'
monitor_already_stopped = 'ℹ️ Monitoring not started'
monitor_restart = '⚠️ Monitoring was stopped.' \
                  '\nClick here to restart -> /'\
                  + common_str.start_mining_monitoring

cancel = '❌ Close'
cancelled = '❌ Closed'

select_curr = '✅ Select the currency'

lang_e = '❌ This language has already been selected'

mining_algo = '💎 Mining algorithms: '
workers_active = '⛏ Active workers: '
profit_per_day = '📈 Profit per day: '
unpaid = '💰 Unpaid balance: '

forbidden = '❌ Access is denied'

addr_set = '✏️ Enter BTC-address'
addr_ok = '🆗'
addr_invalid = '❌ Invalid address'
addr_enter_new = 'Try again' + ' /' + common_str.set_address

what_do = '💫 Select an action'

keyboard_data = 'ℹ️ Info'
keyboard_start_monitor = '▶️ Start monitoring'
keyboard_stop_monitor = '⏹ Stop monitoring'
keyboard_first_set_address = '🔧 Set BTC-address'
keyboard_set_address = '🔁 Change BTC-address'
keyboard_set_currency = '🔁 Change currency'
keyboard_set_language = '🔁 Change language'
keyboard_set_monitor_n = '🔔 Monitor notifications'

notification_set_menu_msg = '🔔⚙'
notification_true = '🔔 '
notification_false = '🔕 '

set_notification_workers = 'Workers'
set_notification_profit_min = 'min profit'
set_notification_profit_max = 'max profit'

notification_profit_help = 'Minimum profit threshold\nSpecify in the selected currency\nType 0 to disable'
notification_profit_error = 'You only need to enter an integer or fractional number'
notification_profit_ok = 'OK'
notification_profit_min_alert = 'Profit fell below the threshold'
notification_profit_min_no = 'The profit has returned for a threshold of a minimum'

notification_workers_disabled = '🔕 Notifications about workers are disabled'
notification_workers_enabled = '🔔 Notifications about workers are enabled'
notification_profit_min_disabled = '🔕 The notification of the minimum profit threshold is off'
notification_profit_max_disabled = '🔕 The notification of the maximum profit threshold is off'
