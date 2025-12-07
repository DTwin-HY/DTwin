# Testing & Code style

## Backend
* The backend uses Pytest and Codecov for testing and Black, isort and pylint for formatting and linting.
* To run the tests for the backend, you can use the command `poetry run pytest`. To also generate a coverage report, you can use the command `poetry run pytest --cov=. --cov-report=html`.
* To format and lint the code, use the commands `poetry run black`, `poetry run isort`, and `poetry run pylint`.
