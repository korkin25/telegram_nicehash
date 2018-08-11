# Этот файл нужен для того чтобы процесс python3 main.py не имел PID 1 внутри контейнера Docker
# Иначе перезапуск процесса через ./restart.sh будет невозможен

from subprocess import Popen
from sys import argv

args_l = argv
del args_l[0]
args_str = ' '.join(args_l)
Popen("python3 main.py" + ' ' + args_str, shell=True)

while True:
	pass
