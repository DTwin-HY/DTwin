[![codecov](https://codecov.io/gh/DTwin-HY/DTwin/graph/badge.svg)](https://app.codecov.io/github/DTwin-HY/DTwin)
[![Run backend tests](https://github.com/DTwin-HY/DTwin/actions/workflows/main.yml/badge.svg)](https://github.com/DTwin-HY/DTwin/actions/workflows/main.yml)

# DTwin

A digital twin project based on LangChain and LangGraph. This is a student-made exploratory project to replicate the workings of a business using agentic networks. The network can pull on a company's data and answer user queries of the data and conduct simple analysis of how business variables interact. The purpose of the network is to support decision making in companies by allowing decision makers easy access to data and analysis from a single source.

The app consists of several standalone agents that are built on top of LangChain's agent framework. These agents are combined in a graph structure to create a network capable of answering complex business queries using LangGraph.

A more thorough explanation of the agents and the network can be found [here](docs/features.md).

This project was developed during the University of Helsinki BSc Computer Science course [TKT20007 Software Lab](https://www.helsinki.fi/en/innovations-and-cooperation/innovations-and-entrepreneurship/business-collaboration-and-partnership/benefit-expertise-our-students/software-engineering-project).

## Links

* [Backlog](https://github.com/orgs/DTwin-HY/projects/1)
* [Issues](https://github.com/DTwin-HY/DTwin/issues)
* [MCP Weather Server module](https://github.com/jensjvh/mcp_historical_weather_server)

## Documentation

* [Agent overview](docs/features.md)
* [API documentation](./docs/api.md)
* [Setting up a local environment](docs/local_deployment.md)
* [Deployment & Software architecture](./docs/architecture.md)
* [Testing & Code style](./docs/testing.md)
* [Project workflow & branching strategy](./docs/branching.md)
* [Definition of Done](./docs/dod.md)

## How to contribute
* Read the instructions below for setting up a local development environment. Basic knowledge of Docker and containers is necessary.
* The preferred development workflow is described [here](./docs/branching.md). In short, when working on a new feature create a new branch, commit your changes and create a pull request to the main branch. Let someone else review your changes before merging. See [issues](https://github.com/DTwin-HY/DTwin/issues) to find something to work on.

