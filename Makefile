setup:
	python3 -m venv .venv

install:
	python3 -m pip install --upgrade pip &&\
		python3 -m pip install -r requirements.txt

test:
	python3 -m pytest tests/*.py

lint:
	python3 -m pylint dlt_transformipy/dlt_transformipy.py

all: install lint test