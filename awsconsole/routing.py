# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('dashboard', '/')
    config.add_route('dashboard.edit', '/dashboard/edit')
    config.add_route('dashboard.save', '/dashboard/save')
    config.add_route('api.start', '/api/start')
    config.add_route('api.stop', '/api/stop')
    config.add_route('api.sync', '/api/sync')
