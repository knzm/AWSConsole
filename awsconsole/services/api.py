# -*- coding: utf-8 -*-

import transaction

from awsconsole import models
from awsconsole.services.aws import (
    AWSServiceError,
    EC2Service,
    Route53Service,
    )

__all__ = ['APIError', 'update_model', 'start_instance']


class APIError(Exception):
    pass


# pretty alias for users who prefer api.Error, not api.APIError
Error = APIError


def update_all_model(request):
    ec2_service = request.context.get_ec2_service()
    for region in ec2_service.get_all_regions():
        update_model(request, region)


def update_model(request, region):
    ec2_service = request.context.get_ec2_service()

    instances = {}
    for instance in ec2_service.get_all_instances(region):
        instances[instance.id] = instance

    volumes = {}
    for volume in ec2_service.get_all_volumes(region):
        volumes[volume.id] = volume

    with transaction.manager:
        cached_instances = {}
        unused_instances = {}
        instance_query = models.DBSession.query(models.InstanceModel) \
            .filter_by(region=region, is_obsolete=False)
        for instance in instance_query:
            unused_instances[instance.instance_id] = instance
        for instance in instances.values():
            cached_instance = models.InstanceModel.update_cache(
                unused_instances.pop(instance.id, None), instance)
            models.DBSession.add(cached_instance)
            cached_instances[instance.id] = cached_instance
        for instance in unused_instances.values():
            instance.is_obsolete = True

        cached_volumes = {}
        unused_volumes = {}
        volume_query = models.DBSession.query(models.VolumeModel) \
            .filter_by(region=region, is_obsolete=False)
        for volume in volume_query:
            unused_volumes[volume.volume_id] = volume
        for volume in volumes.values():
            cached_volume = models.VolumeModel.update_cache(
                unused_volumes.pop(volume.id, None), volume)
            models.DBSession.add(cached_volume)
            cached_volumes[volume.id] = cached_volume
        for volume in unused_volumes.values():
            volume.is_obsolete = True

        for volume in cached_volumes.values():
            volume.instance = None
        for instance in instances.values():
            for block_device_type in instance.block_device_mapping.values():
                cached_volume = cached_volumes[block_device_type.volume_id]
                cached_volume.instance = cached_instances[instance.id]


def start_instance(request, instance_id):
    query = models.DBSession.query(models.InstanceModel)
    instance = query.filter_by(instance_id=instance_id).first()
    if instance is None:
        raise APIError
    ec2_service = request.context.get_ec2_service()
    try:
        return ec2_service.start_instance(instance.region, instance.instance_id)
    except AWSServiceError, ex:
        raise APIError(ex)


def stop_instance(request, instance_id):
    query = models.DBSession.query(models.InstanceModel)
    instance = query.filter_by(instance_id=instance_id).first()
    if instance is None:
        raise APIError
    ec2_service = request.context.get_ec2_service()
    try:
        return ec2_service.stop_instance(instance.region, instance.instance_id)
    except AWSServiceError, ex:
        raise APIError(ex)
