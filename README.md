[![codecov](https://codecov.io/gh/DTwin-HY/DTwin/graph/badge.svg)](https://app.codecov.io/github/DTwin-HY/DTwin)
[![Run backend tests](https://github.com/DTwin-HY/DTwin/actions/workflows/main.yml/badge.svg)](https://github.com/DTwin-HY/DTwin/actions/workflows/main.yml)

# DTwin

A LangGraph digital twin project.

## Links

* [Backlog](https://github.com/orgs/DTwin-HY/projects/1)

## Documentation

* [API documentation](./docs/api.md)
* [Software architecture](./docs/architecture.md)

## Setting up the development environment locally

### Backend

This application uses a Postgres database to store information. You can install a local version from [here](https://www.postgresql.org/download/). You must set up a database to use with this project.

The backend requires a ```.env``` file in the root of the project to work, it should contain the following information:

```
OPENAI_API_KEY= INSERT YOUR API KEY HERE
TAVILY_API_KEY= INSERT YOUR API KEY HERE
SECRET_KEY= INSERT A SECRET KEY HERE
DATABASE_URL=postgresql://YOUR_USERNAME:PASSWORD@localhost:PORTNUMBER/DB_NAME
```
You need an OpenAI API-key for the application to work. The secret key should be generated safely, e.g. using the ```secrets``` python module.

Dependency management is handled by Poetry. To install the required dependencies you need to have Poetry on your machine, please see the installation instructions [here](https://python-poetry.org/docs/).

To start using the backend:
1. Run ```poetry install``` in your terminal to install the project dependencies defined in ```pyproject.toml```
2. Run ```poetry run back``` in your terminal to start the Flask development server


### Frontend


The frontend of the project is made in React + Vite. Dependency management is done through ```npm```. If you do not have it installed, please see [here](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).

The frontend requires a ```.env``` file located in the root of the frontend folder. It should contain ```VITE_BACKEND_URL=http://localhost:5000``` to allow the connection between the frontend and the backend.


To start:

1. Run  ```npm install``` in your terminal to install the project dependencies as described in the ```package.json```
2. Run ```npm run dev``` to run the frontend development server
3. Navigate to the localhost port provided by Vite to view the site

## Running with Docker

The repo contains ```Dockerfiles``` for building Docker images of the backend server and the frontend React app. The Docker Compose file uses an existing Postgres image as database.


1. To `.env` add the lines (db has to be called dtwin currently) and change the DB url from the local version
```
DATABASE_URL= postgresql://dtwin:USERNAME@db:5432/dtwin
POSTGRES_USER= ...
POSTGRES_PASSWORD= ...
POSTGRES_DB=dtwin
POSTGRES_HOST_AUTH_METHOD=md5
```
2. Make sure the services are down with `docker compose down`
3. Run `docker compose build frontend` if the frontend has been updated.
4. Run `docker compose up --detach` to start the services.
