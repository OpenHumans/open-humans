## open-humans

[![Codeship Status for PersonalGenomesOrg/open-humans](https://codeship.io/projects/6f9dcd90-1b67-0132-e696-7e09bcd93b6c/status)](https://codeship.io/projects/34928)

This repository contains the code for the [Open Humans
Website](http://openhumans.org/).

### The local development environment

#### dependencies

- python >=2.7.10
- pip
- virtualenv (`pip install virtualenv`)
- nodejs 4.x
- npm 3.x
- libpq (`apt-get install libpq` in Debian/Ubuntu)
- postgres (`apt-get install libpq-dev python-dev` and
  `apt-get install postgresql postgresql-contrib` in Debian/Ubuntu)
- memcached (`apt-get install memcached` or `brew install memcached`)
- [LiveReload Chrome extension][live-reload] (changing SASS/CSS files
  automatically updates in the browser)

[live-reload]: https://chrome.google.com/webstore/detail/livereload/jnihajbhpnppcggbcgedagnkighmdlei

#### virtualenv

- `mkvirtualenv open-humans`
- `pip install -r requirements.txt`

In the future, start the virtual environment with:
- `workon open-humans`

And update it after pulling updated code by repeating:
- `pip install -r requirements.txt`

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
    - Also allow this user to create new databases (needed for running tests), e.g.:<br>
      `ALTER USER jdoe CREATEDB;`
    - Quit: `\q`
  - Exit postgres user login: `exit`

#### Set up environment settings

Use `env.example` as a starting point. Copy this to `.env` and modify with your
own settings.

#### Initialize or update the database

Do this at the beginning, and update when pulling updated code by running:

- `./manage.py migrate`

#### Running the development server

- `./manage.py runserver`

#### Running tests

You need to process static files before you can run tests.

1. `./manage.py collectstatic`
2. `./manage.py test`

#### Linting

- flake8
- pep256
- pylint
- eslint (`npm install -g eslint`)
