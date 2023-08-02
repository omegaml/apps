from flask import Blueprint, render_template, Flask, request
from flask_login import login_required, current_user
from sqlalchemy.orm import Session

from helloflask.dbmodels import Base, User


def create_app(server=None, uri=None, **kwargs):
    """
    the script API execution entry point
    :return: result
    """
    import omegaml as om

    app = Blueprint('helloflask', __name__,
                    url_prefix=uri,
                    static_folder='static',
                    template_folder='templates')

    om = om.setup()

    def init_db():
        # call this anywhere you need the db connection
        connection = om.datasets.get('sqldb', raw=True)
        Base.metadata.create_all(connection.engine)
        return connection

    @app.route('/')
    def index():
        return render_template('helloflask/index.html',
                               claims=current_user.claims,
                               current_user=current_user)

    @app.route('/report')
    @login_required
    def report():
        # Beispiel-Tabelle: accp_model_description
        # data = om.datasets.get('sqldb', sql="select * ...")
        import pandas as pd
        import json
        import plotly
        import plotly.express as px

        df = pd.DataFrame({
            'Fruit': ['Apples', 'Oranges', 'Bananas', 'Apples', 'Oranges',
                      'Bananas'],
            'Amount': [4, 1, 2, 2, 4, 5],
            'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
        })
        fig = px.bar(df, x='Fruit', y='Amount', color='City',
                     barmode='group')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('helloflask/report.html', graphJSON=graphJSON)

    @app.route('/update', methods=['GET', 'POST'])
    @login_required
    def update():
        connection = init_db()
        if request.method == 'POST':
            with Session(connection.engine) as session:
                user = User(name=request.form.get('name'),
                            fullname=request.form.get('fullname'))
                session.add(user)
                session.commit()
        all_users = om.datasets.get('sqldb', sql='select * from myapp_user_account')
        return render_template('helloflask/update.html', users=all_users)

    # set any configuration for use when deployed in apphub here
    server.config['APP_TITLE'] = 'omega-ml app'
    # configure claims requirements
    server.config['JWT_CLAIMS_RULES'] = {
        'require': {
            r'.*/report': {
                'sourceGroups': r'user'
            }
        }
    }
    server.config['APPHUB_APP_SECURE_NOPROTECT'] = \
        (f'{uri}/?$', '.*/login.*', '.*/logout.*', '.*/authorize', '.*/static/.*', '.*/healthz')
    # configure permissions
    server.config['APPHUB_PERMISSIONS'] = {
        'admin': ['admin'],
        'power-user': ['user', 'admin'],
        'user': ['user'],
    }
    # omega
    server.config['APPHUB_PERMISSIONS_OMEGA'] = {
        'power-user': {
            'qualifier': 'poweruser',
        }
    }
    return app

if __name__ == '__main__':
    import os
    from helloflask.apphublib import local_testing
    from helloflask.localinit import local_init
    server = Flask(__name__)
    os.environ['OMEGA_CONFIG_FILE'] = '../../config.yml'
    app = create_app(server=server)
    local_testing(server, app, local_init=local_init)
    server.run(port=5001)
