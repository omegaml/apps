import logging
import os
from flask import send_file
from jinja2 import ChoiceLoader, FunctionLoader, PackageLoader

from omegaml.client.userconf import get_omega_from_apikey
from omegaml.store.logging import OmegaLoggingHandler


def load_om(context):
    """
    This is a safe way to load omegaml according to apphub configuration

    :param context: the omegaml context as passed by the apphub Flask starter
    :return: om
    """
    # load omegaml
    if context:
        om = get_omega_from_apikey(userid=context['OMEGA_USERID'],
                                   apikey=context['OMEGA_APIKEY'],
                                   api_url=context.get('OMEGA_RESTAPI_URL'))
    else:
        import omegaml as om
    return om


def add_live_resources(om, app, base_path=None,
                       static_folder=None):
    """
    Load static resources from files stored in om.datasets

    Adds a /resources/<path> URI to the blueprint. To load resources,
    in your templates use

         {{ url_for('.resources', filename='path/to/file.ext') }}

    Resources are loaded in this order:

    1. from om.datasets, using om.datasets.get('files/<folder>/<filename>')
    2. from the local file system <folder>/<filename>

    The default <folder> is app.static_folder, defaults to 'static'

    Files are sent with a cache header according to Flask configuration
    in SEND_FILE_MAX_AGE_DEFAULT.

    Use this feature with caution as it may add to latency.

    :param om: the omega instance
    :param app: the blueprint
    :param base_path: the path in om.datasets to load files, defaults to 'files'
    :param static_folder: the static folder, defaults to 'static'
    """

    base_path = base_path or 'files'
    static_folder = static_folder or os.path.basename(app.static_folder) or 'static'

    def _load_resources(filename):
        om_filename = os.path.join(base_path, static_folder, filename)
        file = om.datasets.get(om_filename)
        if file is None:
            data = app.send_static_file(filename)
        else:
            cache_timeout = app.get_send_file_max_age(filename)
            data = send_file(file, mimetype='application/text', cache_timeout=cache_timeout)
        return data

    app.route('/resources/<path:filename>', endpoint='resources')(_load_resources)


def add_live_templates(om, server, app, base_path=None,
                       template_folder=None,
                       cache_size=0):
    """
    Load templates from files stored in om.datasets

    Adds the jinja ChoiceLoader as the Flask template loader.
    To load a template, use the usual template path, e.g.

        render_template('myapp/index.html')

    You may also leverage cascading templates the same way, e.g.

        {% extends "myapp/base.html" %}

    Templates are loaded in this order:

    1. from om.datasets, using om.datasets.get('files/<folder>/<filename>')
    2. from the local file system <folder>/<filename>

    The default <folder> is app.template_folder (defaults to 'templates')

    Use this feature with caution as it may add to latency.

    :param om: the omega instance
    :param server: the Flask instance
    :param app: the Blueprint instance
    :param base_path: the path in om.datasets to load files, defaults to 'files'
    :param template_folder: the templates folder path, defaults to 'templates'
    :param cache_size: the jinja loader cache, defaults to 0, effectively
       causing recompiling of templates on every access. Set this to a larger
       value to only recompile templates when changed. Note for live loading
       to work with a cache size other than 0, the template must exist in
       om.datasets at the time of application start. If it does not exist and
       the cache size is not 0, Flask will load the packaged template and keep
       this in its cache. With a cache size other than 0, templates are only
       recompiled if the file has actually changed. See jina docs for details.
    """

    base_path = base_path or 'files'
    template_folder = template_folder or os.path.basename(app.template_folder) or 'templates'

    def load_live_template(filename):
        om_filename = '{}/{}/{}'.format(base_path,
                                        template_folder,
                                        filename)
        data = None
        file = om.datasets.get(om_filename)

        if file is not None:
            loaded_md5 = getattr(file, 'md5', None)

            def uptodatefn():
                file = om.datasets.get(om_filename)
                live_md5 = getattr(file, 'md5', None)
                return live_md5 == loaded_md5

            source = file.read().decode('utf8')
            data = source, om_filename, uptodatefn
            file.close()
        return data

    server.jinja_loader = ChoiceLoader([
        FunctionLoader(load_live_template),
        PackageLoader(server.name),
        PackageLoader(app.name),
    ])
    server.jinja_options.update(cache_size=cache_size)


def add_omega_logger(om, server):
    """
    route Flask logging output to om.logger

    To see the log use the om cli

    $ om runtime log -f

    :param om: the omega instance
    :param server: the Flask instance
    """
    handler = OmegaLoggingHandler.setup(logger=logging.getLogger('root'), level='DEBUG')
    [logging.getLogger(l).addHandler(handler) for l in ('werkzeug', 'flask.app', server.name)]
