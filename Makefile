setup:
	python3 -m venv .venv

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python -m pytest tests/*.py

lint:
	pylint dlt_transformipy/dlt_transformipy.py

all: install lint test