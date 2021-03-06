# Contributing

### 1. Set up the precommit linting hook

[black](https://black.readthedocs.io/en/stable/) is utilized to lint the server code

It is recommended to set up a precommit hook to ensure that code is being properly formatted

In the root directory, run

```
cp .githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Note that `black` checks the `pyproject.toml` file in the root directory of the folder passed to it for configuration settings

Upon opening a pull request on `main`, linting checks will be applied with the same settings as the precommit

### 2. Github actions

This project uses [Github Actions](https://docs.github.com/en/actions) to validate all pull requests. To view the pipelines applied to this project, either view the `Actions` tab on Github, or see the yaml config files titled `.github/workflows/*.yml`

### 3. Server Framework

This project uses [Ariadne](https://ariadnegraphql.org/), a schema-first graphql python library.

To enable support of GraphQL Subscriptions, which require asgi servers, we utilize [Django channels](https://channels.readthedocs.io/en/stable/) for the web framework

**Note**

The Ariadne-asgi application is a Starlette object, which breaks several dependencies written for vanilla Django (WSGI) and can make routing slightly tricky. Refer to documentation [here](https://www.starlette.io/)

### 4. GraphQL Endpoints

The websocket endpoint (for GraphQL Subscriptions) is located at `ws://localhost:8000/graphql/`

The http endpoint (for Queries and Mutations) is located at `http://localhost:8000/graphql/`

Django default settings are such that the `/` at the end of the above urls is _mandatory_

**Note**

Ariadne implements [subscriptions-transport-ws](https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md) protocol for GraphQL subscriptions. Unfortunately, this is not a maintained library. Furthermore, as of May 2022 Ariadne has not implemented support for [graphql-ws](https://github.com/enisdenjo/graphql-ws), which is an active library for a similar protocol. Fundamentally, `graphql-ws` and `subscriptions-transport-ws` are different protocols, and as such any clients attempting to access the server with `graphql-ws` for subscriptions will be unsuccessful

### 5. Production server

The production server has Python 3.6.9 and Node js 16.15.1

### 6. Staging

Heroku is utilized as a staging area test. When a PR is merged into `main`, github actions pushes the repo to Heroku for a build and then attempts to ping the graphql endpoint for a health check.

The staging endpoint is located at https://lane-server.herokuapp.com/graphql/

Heroku's file system is "ephemeral", which essentially means any file untracked by github does not persist on the Heroku side. This means that migrations applied to sqlite databases are not saved, data added/removed from sqlite databases via API interactions are not saved, a static security.py file does not persist, etc.

Files related to configuration of Heroku deployment are `Procfile`, `requirements.txt`, `runtime.txt`. The github actions file related to staging deployment primarily just pushes the repo to Heroku (with some environment variables) and runs a health check.

### 7. Databases

LANE utilizes [sqlite](https://www.sqlite.org/index.html) for databases. These are locally hosted files on the production computer, which admittedly is inferior to cloud/external hosting. Unfortunately, attempting to access an externally hosted SQL database conflicts with Lab policy.

LANE has 3 databases:

| Name      | Location              |
| --------- | --------------------- |
| `default` | `db/users.sqlite3`    |
| `data`    | `db/data.sqlite3`     |
| `live`    | `db/liveData.sqlite3` |

`default` stores only user information

`live` is a db that is kept very small in size, only carrying information regarding live runs and active EMS systems.

`data` stores processed data for viewing only on the web app. Large and unprocessed datafiles from experimental systems, such as the fast DAQ system, should have their own separate backup and storage.

In the event that `data` grows to be very large (presumably after years of successful data collection), follow these steps to create a new database

1. Move the old `data` sqlite3 file into your desired storage location (do NOT leave it in the `server` directory)
2. In `server`, activate the venv with `source venv/bin/activate`
3. Run `python manage.py migrate --database=data`

You will now have a new empty data base

**Note on migrations**

During development, changes applied to `models.py` in a django app need to be propagated to all databases. To do so, start the venv and run

```bash
python manage.py makemigrations
python manage.py migrate # No flag needed to apply migrations to default
python manage.py migrate --database=data
python manage.py migrate --database=live
...# repeat for any additional databases
```

Note that the live db is currently in the gitignore. This is so that developers with different live tests will not push undesired data onto one another.

### 8. Unit Tests

This project uses [pytest](https://docs.pytest.org/en/7.1.x/) for unit tests. Upon opening a PR, github actions will run the test suite to check for issues.

To run the test suite in development, simply start the venv and in the root directory run

```bash
pytest test
```
