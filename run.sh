#!/bin/sh

source ./.venv/bin/activate
python3 -m flask --app project/main.py run --debug --port=8080
deactivate
