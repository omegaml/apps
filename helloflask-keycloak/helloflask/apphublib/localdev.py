"""
Copyright (c) one2seven GmbH, makers of omega|ml, http://omegaml.io
"""
import socket

from flask import render_template


def local_testing(server, app, local_init=None):
    import flask
    from werkzeug.utils import redirect
    from flask_login import LoginManager, login_user
    from .users import User, AnonymousUser

    # see https://flask-login.readthedocs.io/en/latest/
    login_manager = LoginManager()
    login_manager.init_app(server)
    login_manager.login_view = '.login'
    login_manager.anonymous_user = AnonymousUser

    @login_manager.user_loader
    def load_user(user_id):
        user = User(user_id)
        return user

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if flask.request.method == 'POST':
            username = flask.request.form.get('username')
            if username in flask.current_app.config['USER_CLAIMS']:
                user = User(username)
                login_user(user)
                return redirect(flask.url_for('.index'))
        return render_template('apphub/login.html')

    @app.route('/logout')
    def logout():
        from flask_login import logout_user
        logout_user()
        return redirect(flask.url_for('.index'))

    # set any (local) configuration you like here
    # -- app title used in base.html
    server.config.setdefault('APP_TITLE', 'omega-ml app')
    # -- flask secret key
    server.config['SECRET_KEY'] = (server.config.get('SECRET_KEY') or
                                   socket.gethostname())
    # -- debug template loading
    server.config.setdefault('EXPLAIN_TEMPLATE_LOADING', True)
    # -- the name of the attribute in JWT claims for groups
    server.config.setdefault('JWT_GROUPS_ATTRIBUTE', 'groups')
    # -- claims rules
    #    'path' => { 'groups': ['group1', 'group2'] }
    server.config.setdefault('JWT_CLAIMS_RULES', {
        'required': {
            '/report/.*': {
                'groups': 'user|admin'
            }
        }
    })
    # -- set users to claims mapping (simulates JWT claims locally)
    server.config.setdefault('USER_CLAIMS', {
        'mike': {
            'groups': ['user'],
        },
        'eve': {
            'groups': ['power-user'],
        },
        'admin': {
            'groups': ['admin'],
        }
    })
    # -- permissions for current_user.has_perm(permid) check
    #    permission => ['group1', 'group2']
    server.config.setdefault('APPHUB_PERMISSIONS', {
        'user': ['user'],
        'power-user': ['power-user', 'admin'],
        'admin': ['admin']
    })
    # if true all views will require login and match JWT_CLAIMS_RULES except listed in APPHUB_APP_SECURE_NOPROTECT
    server.config['APPHUB_APP_SECURE_ROUTES'] = server.config.get('APPHUB_APP_SECURE_ROUTES', True)
    # set routes that do not require login, despite APPHUB_APP_SECURE_ROUTES=True
    server.config.setdefault('APPHUB_APP_SECURE_NOPROTECT', ('/$', '.*/login.*', '.*/logout.*',
                                                    '.*/authorize', '.*/static/.*', '.*/healthz'))
    # -- add other local config here or in your local_init()
    server.config['DEBUG'] = True
    # we register the blueprint as this is what apphub does automatically
    server.register_blueprint(app)
    # call local init for user customization
    local_init(server, app) if callable(local_init) else None
    return server
