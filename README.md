## open-humans

[![Codeship Status for OpenHumans/open-humans](https://codeship.com/projects/6f9dcd90-1b67-0132-e696-7e09bcd93b6c/status)](https://codeship.com/projects/34928)
[![codecov.io](https://codecov.io/github/OpenHumans/open-humans/coverage.svg?branch=master)](https://codecov.io/github/OpenHumans/open-humans?branch=master)

This repository contains the code for the [Open Humans
Website](http://openhumans.org/).

### The local development environment

#### dependencies

- python >=3.6
- pip3
- virtualenv (`pip3 install virtualenv`)
- nodejs 6.x
- npm 3.x
- libffi (`apt-get install libffi-dev` in Debian/Ubuntu or `brew install libffi` in OSX)
- libpq (`apt-get install libpq` in Debian/Ubuntu or `brew install libpq` in OSX)
- postgres (`apt-get install libpq-dev python3-dev` and
  `apt-get install postgresql postgresql-contrib` in Debian/Ubuntu)
- memcached (`apt-get install memcached libmemcached-dev` or `brew install memcached`)
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) for
  Selenium tests

[live-reload]: https://chrome.google.com/webstore/detail/livereload/jnihajbhpnppcggbcgedagnkighmdlei

#### virtualenv

For the following commands, you'll also want to set up virtualenvwrapper:
- `pip3 install virtualenvwrapper`
- Follow setup instructions here (e.g. modify your `.bashrc` as needed): http://virtualenvwrapper.readthedocs.io/en/latest/install.html

Create a virtualenv for Python 3.6, e.g.:
- `mkvirtualenv open-humans --python=/usr/bin/python3.6`
- `pip3 install -r requirements.txt -r dev-requirements.txt`

In the future, start the virtual environment with:
- `workon open-humans`

And update it after pulling updated code by repeating:
- `pip3 install -r requirements.txt -r dev-requirements.txt`

#### node.js dependencies (primarily for `gulp`)

- `npm install -g gulp`
- `npm install`

Update after pulling updated code by repeating:
- `npm install`

#### create your postgres database

Running this site requires a PostgreSQL database (even for local development).

- In Debian/Ubuntu
  - Become the postgres user: `sudo su - postgres`
  - Create a database (example name 'mydb'): `createdb mydb`
  - Create a user (example user 'jdoe'): `createuser -P jdoe`
  - Enter the password at prompt (example password: 'pa55wd')
  - run PostgreSQL command line: `psql`
    - Give this user privileges on this database, e.g.:<br>
      `GRANT ALL PRIVILEGES ON DATABASE mydb TO jdoe;`
    - Also allow this user to create new databases (needed for running tests),
      e.g.:<br>
      `ALTER USER jdoe CREATEDB;`
    - Quit: `\q`
  - Exit postgres user login: `exit`

#### Set up environment settings

Use `env.example` as a starting point. Copy this to `.env` and modify with your
own settings.

#### Initialize or update the database

Do this at the beginning, and update when pulling updated code by running:

- `./manage.py migrate`

#### Additional setup

For additional setup information see [docs/SETUP.md](docs/SETUP.md).

#### Running the development server

- `./manage.py runserver`

#### Running tests

You need to process static files before you can run tests.

1. `./manage.py collectstatic`
2. `./manage.py test`

#### Linting & formatting

Please use `black` to format code prior to commits. Set up a
pre-commit hook by running the following:

1. `pre-commit install`
