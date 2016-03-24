#!/usr/bin/env python

import click

from flask import Flask, redirect, request, session, url_for
from flask.ext.oauth import OAuth


@click.command()
@click.option('--client-id')
@click.option('--client-secret')
@click.option('--remote-url')
@click.option('--local-port', default=8001)
def run_oauth2_consumer(client_id, client_secret, remote_url, local_port):
    app = Flask(__name__)
    app.secret_key = 'testing'

    oauth = OAuth()

    open_humans = oauth.remote_app(
        'open_humans',

        base_url='{0}/api/'.format(remote_url),

        authorize_url=('{0}/direct-sharing/projects/oauth2/authorize/').format(
            remote_url),

        access_token_method='POST',
        access_token_params={
            'grant_type': 'authorization_code',
            'redirect_uri':
                ('http://localhost:{0}/oauth-authorize'
                 .format(local_port))
        },
        access_token_url='{0}/oauth2/token/'.format(remote_url),

        request_token_url=None,

        consumer_key=client_id,
        consumer_secret=client_secret)

    @app.route('/')
    def index():
        return 'hello world'

    @app.route('/oauth-authorize')
    @open_humans.authorized_handler
    def oauth_authorized(resp):
        next_url = request.args.get('next') or url_for('index')

        session['open_humans_access_token'] = resp['access_token']
        session['open_humans_refresh_token'] = resp['refresh_token']

        return redirect(next_url)

    @open_humans.tokengetter
    def get_open_humans_token(token):
        return session.get('open_humans_access_token')

    app.run(port=local_port, debug=True, use_reloader=False)


if __name__ == '__main__':
    run_oauth2_consumer()
