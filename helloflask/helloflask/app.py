from flask import Blueprint, Flask, render_template
from werkzeug.utils import redirect


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

    # optional, only use if you need it
    from helloflask import optional
    # om = optional.load_om(context)
    # optional.add_live_resources(om, app)
    # optional.add_live_templates(om, server, app)
    # optional.add_omega_logger(om, server)

    server.register_blueprint(app)
    return app


if __name__ == '__main__':
    server = Flask(__name__)


    @server.route('/')
    def index():
        return redirect('/app')


    app = create_app(server=server, uri='/app')
    server.run()
