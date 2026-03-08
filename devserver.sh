#!/bin/bash

source .venv/bin/activate

export FLASK_APP=main.py

# Set a default port if not provided
PORT=${PORT:-8080}

flask run --host=0.0.0.0 --port=$PORT