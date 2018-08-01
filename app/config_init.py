import configparser

def create_config(path):
    config = configparser.ConfigParser()
    config.add_section('settings')
    config.set('settings', 'token', '')
    config.set('settings', 'msg_id', '0')
    config.set('settings', 'language', '')
    config.set('settings', 'address', '')
    config.set('settings', 'currency', 'USD')
    config.set('settings', 'interval_s', '10')
    config.set('settings', 'monitor', '0')

    with open(path, 'w') as config_file:
        config.write(config_file)


path = 'settings.ini'
create_config(path)
