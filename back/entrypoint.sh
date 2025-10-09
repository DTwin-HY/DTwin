#!/bin/sh

echo "Running db migrations..."
flask --app src/index.py db upgrade

echo "Starting backend server..."
exec gunicorn --config gunicorn_config.py src.index:app