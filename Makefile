.PHONY: update install run

update:
	python update.py

install:
	pip install -r requirements.txt

run:
	python mangaxyz.py