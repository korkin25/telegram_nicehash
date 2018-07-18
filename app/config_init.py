import configparser

token = '4564564645:AAEwBrF2DgVtnwzfHNtgdfPQEElFR4ckKc'


def create_config(path):
	config = configparser.ConfigParser()
	config.add_section('Settings')
	config.set('Settings', 'token', token)
	config.set('Settings', 'msg_id', '0')
	config.set('Settings', 'address', '3MLnyrNo3yoAS8a2YdD7AU2638AGZJKbyh')
	config.set('Settings', 'currency', 'RUB')

	with open(path, 'w') as config_file:
		config.write(config_file)

path = 'Settings.ini'
create_config(path)
