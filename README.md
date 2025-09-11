# DTwin

A LangGraph digital twin project.

## Links

* [Backlog](https://github.com/orgs/DTwin-HY/projects/1)

## Running with Docker

TODO: Alembic for DB migrations, move images to Docker Hub, database name stays as 'dtwin'
1. To `.env` add the lines (db has to be called dtwin currently)
```
DATABASE_URL=

POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=dtwin
POSTGRES_HOST_AUTH_METHOD=md5
```
2. Make sure the services are down with `docker compose down`
3. Run `docker compose build frontend` if the frontend has been updated.
4. Run `docker compose up --detach` to start the services.
