import configparser

token = '4564564645:AAEwBrF2DgVtnwzfHNtgdfPQEElFR4ckKc'


def createConfig(path):
	config = configparser.ConfigParser()
	config.add_section('Settings')
	config.set('Settings', 'token', token)
	config.set('Settings', 'msg_id', '0')

	with open(path, 'w') as config_file:
		config.write(config_file)


path = 'Settings.ini'
createConfig(path)
