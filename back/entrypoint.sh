#!/bin/sh

echo "Running db migrations..."
flask --app main/index.py db upgrade

echo "Starting backend server..."
exec gunicorn --config gunicorn_config.py main.index:app