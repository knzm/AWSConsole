# -*- coding: utf-8 -*-

from pyramid import httpexceptions as exc
from pyramid.view import view_config

from awsconsole import models
from awsconsole.services import api


@view_config(route_name='api.start', renderer='json')
def start_view(request):
    try:
        result = api.start_instance(request, request.params.get('id'))
    except api.Error:
        raise exc.HTTPBadRequest()
    return {"result": "ok"}


@view_config(route_name='api.stop', renderer='json')
def stop_view(request):
    try:
        result = api.stop_instance(request, request.params.get('id'))
    except api.Error:
        raise exc.HTTPBadRequest()
    return {"result": "ok"}


@view_config(route_name='api.sync', renderer='json')
def sync_region_view(request):
    try:
        result = api.sync_region(request, request.params.get('region'))
    except api.Error:
        raise exc.HTTPBadRequest()
    return {"result": "ok"}
