[![codecov](https://codecov.io/gh/DTwin-HY/DTwin/graph/badge.svg)](https://app.codecov.io/github/DTwin-HY/DTwin)
![Run backend tests](https://github.com/DTwin-HY/DTwin/actions/workflows/main.yml/badge.svg)

# Testing & Code style

This project is an exploratory proof of concept app and therefore, development has been done with a features first philosophy.Testing has been conducted on those parts of the project which have some permanence but for many parts, due to the rapidly changing structure of the project, no tests have been made yet.

Project testing coverage can be seen from the Codecov badge and by clicking the badge, a full coverage report is available. Note that some parts of the application have been purposefully omitted due to their still ongoing development.

The project does not currently have any formal end-to-end tests and development has largely rested on manual testing by developers. Once the project nears maturity and a proper release, formal E2E testing would be prudent.

## Backend
The backend uses Pytest and Codecov for testing and Black, isort and pylint for formatting and linting. Unit tests cover most of the stable backend business logic functions, although some newer functions or those pending change are not covered as a rapid development pace was critical during the project.


* To run the tests for the backend, you can use the command `poetry run pytest`. To also generate a coverage report, you can use the command `poetry run pytest --cov=. --cov-report=html`.
* To format and lint the code, use the commands `poetry run black`, `poetry run isort`, and `poetry run pylint`.

## Frontend

This project uses ESLint to lint code and Prettier to format code, to manage code style for the frontend.

* To lint the project use the command `npm run lint`
* To format the files use the command `npm run format`