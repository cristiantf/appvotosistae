@echo off
set FLASK_APP=main.py
.venv\Scripts\python.exe -m flask run --host=127.0.0.1 --port=5000 --debug
