from flask import Blueprint, Response
from time import sleep


def create_api_blueprint(uri):
    bp = Blueprint('api', __name__, url_prefix=uri)

    @bp.route('/api/test/streaming')
    def streaming():
        def generate():
            for i in range(100):
                sleep(1)
                yield 'waiting'
            yield 'done'

        return Response(generate(), mimetype='text/csv')

    @bp.route('/api/test/blocking')
    def blocking():
        sleep(100)
        return Response('done', mimetype='text/csv')

    return bp


def create_app(context=None, server=None, uri=None, **kwargs):
    """
    the script API execution entry point
    :return: result
    """

    import dash
    import dash_core_components as dcc
    import dash_html_components as html

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, server=server, url_base_pathname=uri,
                    external_stylesheets=external_stylesheets)

    # data = om.datasets.get('sales')

    import omegaml as om

    app.layout = html.Div(children=[
        html.H1(children='Hello Dash'),

        html.Div(children='''
            omega ml apphub - demo helloworld
        '''),

        html.Div(html.P("datasets {}".format(om.datasets.list()))),

        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
                ],
                'layout': {
                    'title': 'Dash Data Visualization'
                }
            }
        )
    ])

    bp = create_api_blueprint(uri)
    app.server.register_blueprint(bp)

    return app


if __name__ == '__main__':
    app = create_app(server=True)
    app.run_server()
