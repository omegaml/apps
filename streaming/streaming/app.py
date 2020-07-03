"""
this implements a very simple streaming application and UI with processed data

Purpose:
    1. take data from a minibatch streaming source
    2. process the data and store in an omegaml dataset
    3. display the dataset in the UI

Usage:
    # start consumer app locally
    $ python streaming/app.py

    # separate producer session
    $ om shell
    [] import minibatch as mb
       stream = mb.stream('test', url=om.defaults.OMEGA_MONGO_URL)
       stream.append(dict(foo='bar'))

    # see the data flowing in by refreshing on
    http://localhost:5000/

    Note the same works regardless of the actual location of the streaming/app.py
    and the producer session, as long as both are connected to the same omega|ml
    server. We can of course make the producer independent of an omega|ml connection
    by making the consumer app from a source external to omega|ml such as Kafka or MQTT,
    and have the producer write to these sources:

    $ producer python
    [] sink = KafkaSink('topic')
       sink.put(message)

    For this to work, change the DataSource below with KafkaSource('topic')

    The above examples use omega|ml and Kafka run locally.

    # run a Kafka broker locally
    $ docker-compose -f minibatch/resources/docker-compose-kafka up

    # run omegaml locally (specify [mongodb] without brackets for a minimum setup)
    $ docker-compose -f omegaml/docker-compose.yml up [mongodb]
"""
from minibatch.contrib.apps.omegaml import StreamingApp

def create_app(context=None, server=None, uri=None, **kwargs):
    app = StreamingApp(server=server, uri=uri)

    # add any routes you like, will be served at <uri>/<route>
    @app.route('/')
    def index():
        import omegaml as om
        return '{}'.format(om.datasets.get('test-stream'))

    # if you added routes, register the blueprint
    app.server.register_blueprint(app)

    # start the minibatch consumer
    app.start_streaming(consumer)
    return app


def consumer(url=None):
    # this is the consumer implementation, i.e. the @streaming function
    from minibatch import streaming

    # you may add a source or just rely on some producer to write to the stream
    # may also add a sink if you like or just store the data somehow else
    # note that the @streaming processing function is run in parallel on an executor pool of processes
    @streaming('test', url=url)
    def processing(window):
        import omegaml as om
        om.datasets.put(window.data, 'test-stream')


if __name__ == '__main__':
    app = create_app(server=True)
    app.run()
    app.stop()
