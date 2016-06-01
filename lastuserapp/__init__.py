# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.rq import RQ
import coaster.app
from baseframe import baseframe, assets, Version

import lastuser_core
import lastuser_oauth
import lastuser_ui
from lastuser_core import login_registry
from lastuser_core.models import db
from lastuser_oauth import providers
from ._version import __version__

version = Version(__version__)
app = Flask(__name__, instance_relative_config=True)

app.register_blueprint(lastuser_core.lastuser_core)
app.register_blueprint(lastuser_oauth.lastuser_oauth)
app.register_blueprint(lastuser_ui.lastuser_ui)


from . import views  # NOQA

assets['lastuser-oauth.js'][version] = lastuser_oauth.lastuser_oauth_js,
assets['lastuser-oauth.css'][version] = lastuser_oauth.lastuser_oauth_css


def init_for(env):
    coaster.app.init_app(app, env)
    db.init_app(app)
    db.app = app  # To make it work without an app context
    RQ(app)  # Pick up RQ configuration from the app
    baseframe.init_app(app, requires=['lastuser-oauth'],
        ext_requires=['baseframe-bs3', 'fontawesome>=4.3.0', 'jquery.cookie', 'timezone'],
        enable_csrf=True)

    lastuser_oauth.lastuser_oauth.init_app(app)
    lastuser_oauth.mailclient.mail.init_app(app)
    lastuser_oauth.views.login.oid.init_app(app)

    # Register some login providers
    if app.config.get('OAUTH_TWITTER_KEY') and app.config.get('OAUTH_TWITTER_SECRET'):
        login_registry['twitter'] = providers.TwitterProvider('twitter', 'Twitter',
            at_login=True, priority=True, icon='twitter',
            key=app.config['OAUTH_TWITTER_KEY'],
            secret=app.config['OAUTH_TWITTER_SECRET'],
            access_key=app.config.get('OAUTH_TWITTER_ACCESS_KEY'),
            access_secret=app.config.get('OAUTH_TWITTER_ACCESS_SECRET'))
    if app.config.get('OAUTH_GOOGLE_KEY') and app.config.get('OAUTH_GOOGLE_SECRET'):
        login_registry['google'] = providers.GoogleProvider('google', 'Google',
            client_id=app.config['OAUTH_GOOGLE_KEY'],
            secret=app.config['OAUTH_GOOGLE_SECRET'],
            scope=app.config.get('OAUTH_GOOGLE_SCOPE', ['email', 'profile']),
            at_login=True, priority=True, icon='google')
    if app.config.get('OAUTH_LINKEDIN_KEY') and app.config.get('OAUTH_LINKEDIN_SECRET'):
        login_registry['linkedin'] = providers.LinkedInProvider('linkedin', 'LinkedIn',
            at_login=True, priority=False, icon='linkedin',
            key=app.config['OAUTH_LINKEDIN_KEY'],
            secret=app.config['OAUTH_LINKEDIN_SECRET'])
    if app.config.get('OAUTH_GITHUB_KEY') and app.config.get('OAUTH_GITHUB_SECRET'):
        login_registry['github'] = providers.GitHubProvider('github', 'GitHub',
            at_login=True, priority=False, icon='github',
            key=app.config['OAUTH_GITHUB_KEY'],
            secret=app.config['OAUTH_GITHUB_SECRET'])
    login_registry['openid'] = providers.OpenIdProvider('openid', 'OpenID',
        at_login=True, priority=False, icon='openid')
