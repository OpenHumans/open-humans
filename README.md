## open-humans

This repository contains the code that will eventually live on the [Open Humans
Website](http://openhumans.org/).

### The local development environment

#### dependencies

- python
- pylint, flake8
- pip
- virtualenv (`pip install virtualenv`)
- nodejs
- eslint (`npm install -g eslint`)
- [LiveReload Chrome extension][live-reload] (changing SASS/CSS files
  automatically updates in the browser)

[live-reload]: https://chrome.google.com/webstore/detail/livereload/jnihajbhpnppcggbcgedagnkighmdlei

#### virtualenv

- `mkvirtualenv open-humans`
- `pip install -r requirements.txt`

#### node.js dependencies (primarily for `gulp`)

- `npm install -g gulp`
- `npm install`

#### Running the development server

- `./manage.py runserver`
