run:
	racket supervisor.rkt config.json
virtualenv:
	virtualenv dev
setup:
	pip install -r requirements.txt
clean:
	rm -rf botdata/
test:
	sh tests.sh
copy_keys:
	scp -r keys steve@alarmpi:~/discord-bots
