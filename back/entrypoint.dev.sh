#!/bin/sh -eu

echo "Running db migrations..."
flask --app src/index.py db upgrade

echo "Populating db..."
poetry run python3 -m src.data_scripts.storage_data_generator
poetry run python3 -m src.data_scripts.sales_data_generator
poetry run python3 -m src.data_scripts.customer_data_generator

echo "Starting backend server..."
exec flask run --host 0.0.0.0 --port 5000 --reload