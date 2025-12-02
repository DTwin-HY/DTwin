#!/bin/sh

echo "Running db migrations..."
flask --app src/index.py db upgrade

echo "Populating db..."
poetry run python3 -m src.data_scripts.storage_data_generator
poetry run python3 -m src.data_scripts.sales_data_generator
poetry run python3 -m src.data_scripts.customer_data_generator

echo "Creating required folder structure..."
mkdir -p /app/dataframes
chmod -R a+rw /app/dataframes

echo "Starting backend server..."
exec gunicorn --config gunicorn_config.py src.index:app