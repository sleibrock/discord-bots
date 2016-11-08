run:
	racket launcher.rkt
virtualenv:
	virtualenv dev
dev:
	source dev/bin/activate
setup:
	pip install -r requirements.txt
copy_keys:
	scp -r keys steve@alarmpi:~/discord-bots
