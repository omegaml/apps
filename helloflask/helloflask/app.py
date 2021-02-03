import logging
from flask import Blueprint, render_template, Flask

from omegaml.store.logging import OmegaLoggingHandler


def create_app(context=None, server=None, uri=None, **kwargs):
    """
    the script API execution entry point

    Args:
        context (dict): the omegaml context
        server (Flask): the Flask() instance
        uri (str): the base uri of the application on apphub
    """

    # setup blueprint with template and static paths
    # https://flask.palletsprojects.com/en/1.1.x/blueprints/#static-files
    # https://flask.palletsprojects.com/en/1.1.x/blueprints/#templates
    app = Blueprint('helloflask', __name__,
                    url_prefix=uri,
                    static_folder='static',
                    template_folder='templates')

    # all routes will be served at uri + route
    # e.g. /foo will be served at uri/foo
    @app.route('/')
    def index():
        return render_template('helloflask/index.html')

    server.register_blueprint(app)

    handler = OmegaLoggingHandler.setup(logger=logging.getLogger('root'), level='DEBUG')
    [logging.getLogger(l).addHandler(handler) for l in ('werkzeug', 'flask.app', server.name)]
    return app


if __name__ == '__main__':
    server = Flask(__name__)
    app = create_app(server=server)
    server.run()
