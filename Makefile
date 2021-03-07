setup:
	python3 -m venv .venv

install:
	python3 -m pip install --upgrade pip &&\
		python3 -m pip install -r requirements.txt

test:
	python3 -m pytest -s tests/*.py

lint:
	python3 -m pylint dlt_transformipy

all: install lint test