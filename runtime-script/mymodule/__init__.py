

def run(om, *args, **kwargs):
    om.logger.info('hello from mymodule')
    print(__file__)
    return {'datasets': om.datasets.list(), 'models': om.datasets.list()}
