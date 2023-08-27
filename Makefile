PIP = $(shell which pip)
PYTHON = $(shell which python3)
SURREAL = $(shell which surreal)
PORT = 8000

all: clean setup run
	
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-build: 
	rm -fr build/
	rm -fr dist/

clean: clean-build clean-pyc

setup: requirements.txt
	$(PIP) install -r $<

run:
	echo -e "port: $(PORT)\nuser: 'root'\npass: 'root'\nns: 'wtt'\ndb: 'wtt'" > config/db_config.yaml
	$(SURREAL) start --user root --pass root --bind 0.0.0.0:$(PORT) memory &
	$(SURREAL) import --conn http://localhost:$(PORT) --user root --pass root --ns wt --db wt data/db.surql
	$(PYTHON) src/main.py