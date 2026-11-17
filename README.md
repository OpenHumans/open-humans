## open-humans

[![Codeship Status for OpenHumans/open-humans](https://codeship.com/projects/6f9dcd90-1b67-0132-e696-7e09bcd93b6c/status)](https://codeship.com/projects/34928)
[![codecov.io](https://codecov.io/github/OpenHumans/open-humans/coverage.svg?branch=master)](https://codecov.io/github/OpenHumans/open-humans?branch=master)

This repository contains the code for the [Open Humans
Website](http://openhumans.org/).

### The local development environment

#### dependencies

- Docker with Compose
- [uv](https://docs.astral.sh/uv/) to change Python dependencies
  (`pyproject.toml` and `uv.lock`)
- Node.js 24 and [pnpm](https://pnpm.io/) to build the CSS and JavaScript
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) for
  Selenium tests

`docker compose` runs the web server, the Celery worker, PostgreSQL, and
Redis. The repository is mounted into the containers, so code changes apply
without rebuilding. Rebuild after changing dependencies:

- `docker compose build`

#### CSS and JavaScript

The sources in `static/` are built into `build/`, which Django serves:

- `pnpm install`
- `pnpm build` (or `pnpm watch` to rebuild on changes)

`build.mjs` bundles each script in `static/js/` with esbuild, compiles the
stylesheets with Sass, and copies the third-party libraries (jQuery,
Bootstrap, select2, and others) from `node_modules`. The Docker image runs the
same build and `collectstatic`, and whitenoise serves the result.

#### Set up environment settings

Use `env.example` as a starting point. Copy this to `.env` and modify with your
own settings. Compose supplies `DATABASE_URL` and `REDIS_URL` itself.

#### Initialize or update the database

Do this at the beginning, and update when pulling updated code by running:

- `docker compose run --rm web python manage.py migrate`

#### Additional setup

For additional setup information see [docs/SETUP.md](docs/SETUP.md).

#### Running the development server

- `docker compose up`

The site is served at http://127.0.0.1:8000/.

#### Running tests

- `docker compose run --rm -e NOBROWSER=true web python manage.py test`

Tests that upload to S3 are skipped unless `AWS_S3_STORAGE_BUCKET_NAME` is set.

#### Finding spam

`python manage.py spam_report --output-dir <dir>` writes `accounts.csv` and
`projects.csv` listing accounts and unapproved projects that look like spam.
It only reads. `python manage.py suspend_users --id <ids>` deactivates accounts.

#### Linting & formatting

Please use `black` to format code prior to commits. Set up a
pre-commit hook by running the following:

1. `pre-commit install`
