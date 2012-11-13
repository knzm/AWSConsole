# -*- coding: utf-8 -*-

from .meta import *
from .instance import *


def includeme(config):
    def init_model_directive(config):
        init_model(config.registry.settings)
    config.add_directive('init_model', init_model_directive)
