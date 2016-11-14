run:
	racket run.rkt
virtualenv:
	virtualenv dev
dev:
	source dev/bin/activate
setup:
	pip install -r requirements.txt
	npm install discordie
test:
	raco test -x .
copy_keys:
	scp -r keys steve@alarmpi:~/discord-bots
