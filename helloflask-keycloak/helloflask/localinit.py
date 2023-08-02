import os

import omegaml as om


def local_init(server, app):
    # local settings for testing purpose only
    server.config['JWT_GROUPS_ATTRIBUTE'] = 'groups'
    server.config['APPHUB_PERMISSIONS'] = {
        'admin': ['admin'],
        'power-user': ['power-user', 'admin'],
        'user': ['user'],
    }
    server.config['USER_CLAIMS'] = {
        'mike': {
            'groups': ['user'],
        },
        'eve': {
            'groups': ['power-user'],
        },
        'admin': {
            'groups': ['admin'],
        }
    }

    if not 'sqldb' in om.datasets.list():
        om.datasets.put('sqlite:////tmp/test.sqlite', 'sqldb', replace=True)
