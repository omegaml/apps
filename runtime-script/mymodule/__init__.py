

def run(om, *args, **kwargs):
    om.logger.info('hello from mymodule')
    return {'datasets': om.datasets.list()}
