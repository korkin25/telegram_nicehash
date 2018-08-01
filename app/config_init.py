import configparser

def create_config(path):
    config = configparser.ConfigParser()
    config.add_section('Settings')
    config.set('Settings', 'token', '')
    config.set('Settings', 'msg_id', '0')
    config.set('Settings', 'language', '')
    config.set('Settings', 'address', '')
    config.set('Settings', 'currency', 'USD')

    with open(path, 'w') as config_file:
        config.write(config_file)


path = 'Settings.ini'
create_config(path)
