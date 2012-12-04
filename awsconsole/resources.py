# -*- coding: utf-8 -*-

from operator import itemgetter

from awsconsole.services.aws import EC2Service, Route53Service
from awsconsole import models
from formencode import validators, Schema

__all__ = ['RootContext']

regions = [
    "us-east-1", "us-west-2", "us-west-1", "eu-west-1",
    "ap-southeast-1", "ap-northeast-1", "sa-east-1",
]

region_info = {
    "us-east-1": {"area": "US East", "city": "N. Virginia"},
    "us-west-1": {"area": "US West", "city": "N. California"},
    "us-west-2": {"area": "US West", "city": "Oregon"},
    "eu-west-1": {"area": "EU", "city": "Ireland"},
    "ap-southeast-1": {"area": "Asia Pacific", "city": "Singapore"},
    "ap-northeast-1": {"area": "Asia Pacific", "city": "Tokyo"},
    "sa-east-1": {"area": "South America", "city": "Sao Paulo"},
}

default_region = "ap-northeast-1"


class DashboardSchema(Schema):
    filter_extra_fields = True
    allow_extra_fields = True
    region = validators.OneOf(regions, if_empty=default_region,
                              if_missing=default_region)


class RootContext(object):
    def __init__(self, request):
        self.request = request

    def get_aws_service(self, service_cls):
        settings = self.request.registry.settings
        return service_cls(
            aws_secret_access_key=settings["aws_secret_access_key"],
            aws_access_key_id=settings["aws_access_key_id"])

    def get_ec2_service(self):
        return self.get_aws_service(EC2Service)

    def get_route53_service(self):
        return self.get_aws_service(Route53Service)

    def get_instances(self):
        instances = {}
        instances_per_region = {}
        for instance in models.DBSession.query(models.InstanceModel):
            d = instances_per_region.setdefault(instance.region, {})
            d[instance.instance_id] = instance
            instances[instance.instance_id] = instance.to_dict()
            instances[instance.instance_id]["volumes"] = \
                [volume.to_dict() for volume in instance.get_current_volumes()]
        ec2_service = self.get_ec2_service()
        for region in instances_per_region:
            instance_ids = [instance_id for instance_id, instance \
                                in instances_per_region[region].iteritems()
                            if not instance.is_obsolete]
            for instance in ec2_service.get_instances(
                region, instance_ids=instance_ids):
                if instance.id in instances:
                    instances[instance.id]["state"] = instance.state
        return sorted(instances.values(), key=itemgetter('id'))

    def get_instances_by_region(self, region):
        instances = {}

        query = models.DBSession.query(models.InstanceModel) \
            .filter_by(region=region)
        for instance in query:
            instances[instance.instance_id] = instance.to_dict()
            instances[instance.instance_id]["volumes"] = \
                [volume.to_dict() for volume in instance.get_current_volumes()]

        ec2_service = self.get_ec2_service()
        instance_ids = [instance_id for instance_id, instance \
                            in instances.iteritems()
                        if not instance["is_obsolete"]]
        for instance in ec2_service.get_instances(
            region, instance_ids=instance_ids):
            if instance.id in instances:
                instances[instance.id]["state"] = instance.state

        return sorted(instances.values(), key=itemgetter('id'))

    def area_from_region(self, region):
        return region_info.get(region, {}).get('area')

    def city_from_region(self, region):
        return region_info.get(region, {}).get('city')

    def get_current_region(self):
        schema = DashboardSchema()
        params = schema.to_python(self.request.params)
        return params["region"]
