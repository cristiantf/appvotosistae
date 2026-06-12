#!/bin/bash

export FLASK_APP="main.py"
./.venv/bin/python -m flask run --host=127.0.0.1 --port=5000 --debug
