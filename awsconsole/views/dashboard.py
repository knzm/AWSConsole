# -*- coding: utf-8 -*-

from formencode import validators, Schema
from pyramid.view import view_config
from pyramid import httpexceptions as exc
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer
from js.bootstrap import bootstrap
from js.jqueryui import jqueryui, bootstrap as jqueryui_theme

from awsconsole import models


@view_config(route_name='dashboard', renderer='dashboard.jinja2')
def dashboard_view(request):
    bootstrap.need()
    jqueryui.need()
    jqueryui_theme.need()
    region = request.context.get_current_region()
    instances = request.context.get_instances_by_region(region)
    return {
        "instances": instances,
        "current_region": region,
        }


class DashboardEditView(object):
    class schema(Schema):
        allow_extra_fields = True
        filter_extra_fields = True
        hostnames = validators.String()

    def __init__(self, request):
        self.request = request

    @view_config(route_name='dashboard.edit', renderer='dashboard_edit.jinja2')
    def edit(self):
        instance_id = self.request.params.get('instance_id')
        query = models.DBSession.query(models.InstanceModel)
        instance = query.filter_by(instance_id=instance_id).first()
        if instance is None:
            raise exc.HTTPNotFound()
        form = Form(self.request, schema=self.schema, obj=instance)
        return {"instance": instance, "renderer": FormRenderer(form)}

    @view_config(route_name='dashboard.save', renderer='json')
    def save(self):
        instance_id = self.request.params.get('instance_id')
        query = models.DBSession.query(models.InstanceModel)
        instance = query.filter_by(instance_id=instance_id).first()
        if instance is None:
            raise exc.HTTPNotFound()
        form = Form(self.request, schema=self.schema, obj=instance)
        if not form.validate():
            raise exc.HTTPBadRequest()
        form.bind(instance)
        return {"result": "ok"}
