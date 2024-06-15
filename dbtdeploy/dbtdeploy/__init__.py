def run(om=None, project=None, *args, **kwargs):
    from pathlib import Path
    import subprocess
    dbt_dir = Path(__file__).parent
    project_dir = dbt_dir / project
    cmd = f"dbt run -d --profiles-dir {dbt_dir} --project-dir {project_dir}"
    update_dbt_profile(f"{dbt_dir}/profiles.yml", om=om, **kwargs)
    results = subprocess.run(cmd, shell=True, check=True, capture_output=True)
    return results.stdout.decode('utf-8')


def update_dbt_profile(fn=None, mod=None, om=None, **vars):
    """
    update dbt profiles.yaml with omegaml defaults

    Usage:
        import omegaml as om
        mod = om.scripts.get('dbt/foo', install=True)
        update_dbt_profile(mod=mod, om=om)
    """
    from pathlib import Path
    default_fn = Path(getattr(mod, '__file__', __file__)).parent / 'profiles.yml'
    fn = Path(fn) if fn else default_fn
    if not fn.exists():
        raise FileNotFoundError(f'dbt profiles.yml not found at {fn}')
    vars.update(**om.defaults) if om else None
    with open(fn, 'r') as f:
        profiles = f.read()
    with open(fn, 'w') as f:
        profiles = profiles.format(**vars)
        f.write(profiles)
    return fn.parent


def create_app(server=None, uri=None, **kwargs):
    import os
    import uuid

    from functools import lru_cache
    from flask import Flask, abort
    from flask import Blueprint
    from zipfile import ZipFile

    import omegaml as om

    server = server or Flask(__name__)
    server.config.setdefault('SECRET_KEY', os.environ.get('SECRET_KEY') or uuid.uuid4().hex)

    app = Blueprint('foo', __name__,
                    url_prefix=uri,
                    template_folder='templates')

    file_cache = lru_cache(maxsize=100)
    om = om.setup()

    @app.route('/')
    def index():
        # present a list of project reports stored in om.datasets
        # -- each project report is stored as dbt/<project>/report.zip
        href = "<a href='{uri}/{project}/index'>{project}</a><br>"
        projects = [href.format(project=os.path.basename(os.path.dirname(project)),
                                uri=uri or '') for project in om.datasets.list('dbt/*')]
        text = "<p>select a project to view its dbt report</p>"
        return text + "\n".join(projects) if projects else "No projects found"

    @app.route('/<project>/index')
    def project(project):
        # open the project report's index.html
        _send_report_file.cache_clear()
        project_dir = f'dbt/{project}'
        return _send_report_file(project_dir, 'index.html')

    @app.route('/<project>/<path:path>')
    def static_file(project, path):
        # open a static file from the project report
        project_dir = f'dbt/{project}'
        return _send_report_file(project_dir, path)

    @app.errorhandler(404)
    def handle_exception(e):
        return {
            "code": e.code,
            "description": e.description,
            "exception": str(e),
        }, 404

    @file_cache
    def _send_report_file(project_dir, filename):
        report_fn = f'{project_dir}/report.zip'
        try:
            with om.datasets.get(report_fn) as f:
                zipfile = ZipFile(f)
                data = zipfile.read(f'report/{filename}')
                zipfile.close()
        except Exception as e:
            abort(404, str(e))
        return data

    server.register_blueprint(app)
    return server


