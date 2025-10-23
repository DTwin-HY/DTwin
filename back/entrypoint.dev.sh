#!/bin/sh

echo "Running db migrations..."
flask --app src/index.py db upgrade

echo "Starting backend server..."
exec flask run --host 0.0.0.0 --port 5000 --reload