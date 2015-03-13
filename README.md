## open-humans

[![Codeship Status for PersonalGenomesOrg/open-humans](https://codeship.io/projects/6f9dcd90-1b67-0132-e696-7e09bcd93b6c/status)](https://codeship.io/projects/34928)

This repository contains the code that will eventually live on the [Open Humans
Website](http://openhumans.org/).

### Note!

We have not currently launched and would like to hold off on widely sharing this
codebase or the pre-launch website with the public until we do.

If you'd like pre-launch access you can
[express your interest here](https://docs.google.com/a/personalgenomes.org/forms/d/1AZHXqjvCrOq6bQZYPQ7xsaqmgEUenqAvsiZ2-n3McJM/viewform).

### The local development environment

#### dependencies

- python
- pylint, flake8
- pip
- virtualenv (`pip install virtualenv`)
- nodejs 10.x
- npm 1.4.x
- eslint (`npm install -g eslint`)
- libpq (`apt-get install libpq` in Debian/Ubuntu)
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
