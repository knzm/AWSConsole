# -*- coding: utf-8 -*-

from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(
        settings=settings,
        root_factory='.resources.RootContext')

    # setup model
    config.include('.models')
    config.init_model()

    # setup routing/view
    config.include('.routing')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.scan('.views')

    return config.make_wsgi_app()

