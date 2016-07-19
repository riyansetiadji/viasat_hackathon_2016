.DEFAULT_GOAL := devel

devel:
	python3 threeweeks.py
prod:
	gunicorn --worker-class eventlet -w 1 threeweeks:app
