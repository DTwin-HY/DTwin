[![codecov](https://codecov.io/gh/DTwin-HY/DTwin/graph/badge.svg)](https://app.codecov.io/github/DTwin-HY/DTwin)
[![Run backend tests](https://github.com/DTwin-HY/DTwin/actions/workflows/main.yml/badge.svg)](https://github.com/DTwin-HY/DTwin/actions/workflows/main.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# DTwin

A digital twin project based on LangChain and LangGraph. This is a student-made exploratory project to replicate the workings of a business using agentic networks. The network can pull on a company's data and answer user queries of the data and conduct simple analysis of how business variables interact. The purpose of the network is to support decision making in companies by allowing decision makers easy access to data and analysis from a single source.

The app consists of several standalone agents that are built on top of LangChain's agent framework. These agents are combined in a graph structure to create a network capable of answering complex business queries using LangGraph.

A more thorough explanation of the agents and the network can be found [here](docs/features.md).

This project was developed during the University of Helsinki BSc Computer Science course [TKT20007 Software Lab](https://www.helsinki.fi/en/innovations-and-cooperation/innovations-and-entrepreneurship/business-collaboration-and-partnership/benefit-expertise-our-students/software-engineering-project).

## Links

* [Backlog](https://github.com/orgs/DTwin-HY/projects/1)
* [Issues](https://github.com/DTwin-HY/DTwin/issues)

## Documentation

* [API documentation](./docs/api.md)
* [Project workflow & branching strategy](./docs/branching.md)
* [Definition of Done](./docs/dod.md)
* [Deployment & Software architecture](./docs/architecture.md)
* [Testing & Code style](./docs/testing.md)
* [Agent overview](docs/features.md)

## How to contribute
* Read the instructions below for setting up a local development environment. Basic knowledge of Docker and containers is necessary.
* The preferred development workflow is described [here](./docs/branching.md). In short, when working on a new feature create a new branch, commit your changes and create a pull request to the main branch. Let someone else review your changes before merging. See [issues](https://github.com/DTwin-HY/DTwin/issues) to find something to work on.

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

### Database migrations

* To apply database migrations, run the command `poetry run flask --app src/index.py db upgrade`.
* To create a new migration after a change to the models, run `poetry run flask --app src/index.py db migrate -m "your message here"`.

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
DATABASE_URL= postgresql://dtwin:PASSWORD@db:5432/dtwin
POSTGRES_USER= ...
POSTGRES_PASSWORD= ...
POSTGRES_DB=dtwin
POSTGRES_HOST_AUTH_METHOD=md5
```
2. Make sure the services are down with `docker compose down` (to delete volumes `docker compose down -v`)
3. Run `docker compose up --detach` to start the services (to force rebuild images, `docker compose up --detach --build`).
