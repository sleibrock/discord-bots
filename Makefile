run:
	raco superv config.json
virtualenv:
	virtualenv dev
setup:
	pip install -r requirements.txt
    raco pkg install superv
clean:
	rm -rf botdata/
test:
	sh tests.sh
copy_keys:
	scp -r keys steve@alarmpi:~/discord-bots
