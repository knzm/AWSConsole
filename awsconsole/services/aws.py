# -*- coding: utf-8 -*-

import functools

import boto.ec2
import boto.route53
from boto.exception import EC2ResponseError
from boto.regioninfo import RegionInfo
from boto.route53.record import ResourceRecordSets

__all__ = ['AWSServiceError', 'EC2Service', 'Route53Service']


class AWSServiceError(Exception):
    pass


def check_connection(conn):
    if conn is None:
        raise AWSServiceError("Can't make connection")
    return conn


class exception_checked(object):
    def __init__(self, *exc_classes):
        self.exc_classes = exc_classes

    def __call__(self, func):
        exc_classes = self.exc_classes
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                return func(*args, **kw)
            except exc_classes, ex:
                raise AWSServiceError(ex)
        return wrapper


class AWSService(object):
    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key


class EC2Service(AWSService):
    def get_all_regions(self):
        return boto.ec2.regions(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key)

    def _get_connection(self, region):
        if isinstance(region, boto.regioninfo.RegionInfo):
            region = region.name
        return boto.ec2.connect_to_region(
            region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key)

    def _get_checked_connection(self, region):
        return check_connection(self._get_connection(region))

    @exception_checked(EC2ResponseError)
    def get_all_instances(self, region):
        conn = self._get_checked_connection(region)
        for reservation in conn.get_all_instances():
            for instance in reservation.instances:
                yield instance

    @exception_checked(EC2ResponseError)
    def get_instances(self, region, instance_ids):
        conn = self._get_checked_connection(region)
        return [r.instances[0] for r in conn.get_all_instances(instance_ids)]

    @exception_checked(EC2ResponseError)
    def get_all_volumes(self, region):
        conn = self._get_checked_connection(region)
        return conn.get_all_volumes()

    @exception_checked(EC2ResponseError)
    def get_volumes(self, region, volume_ids):
        conn = self._get_checked_connection(region)
        return conn.get_all_volumes(volume_ids)

    @exception_checked(EC2ResponseError)
    def start_instance(self, region, instance_id):
        conn = self._get_checked_connection(region)
        return conn.start_instances([instance_id])

    @exception_checked(EC2ResponseError)
    def stop_instance(self, region, instance_id):
        conn = self._get_checked_connection(region)
        return conn.stop_instances([instance_id])


class Route53Service(AWSService):
    def _get_connection(self):
        return boto.route53.Route53Connection(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key)

    def _get_checked_connection(self):
        return check_connection(self._get_connection())

    def get_all_hosted_zones(self):
        conn = self._get_checked_connection()
        zones = []
        start_marker = None
        while True:
            result = conn.get_all_hosted_zones(start_marker=start_marker)
            response = result['ListHostedZonesResponse']
            zones += [{'Name': zone['Name'], 'Id': zone['Id']}
                      for zone in response['HostedZones']]
            if response['IsTruncated'] == 'false':
                break
            start_marker = response['NextMarker']
        return zones

    def update_record(self, hosted_zone_id, names, type, resource_records,
                      ttl=600, identifier=None, weight=None, comment=""):
        """Delete and then add a record to a zone"""
        conn = self._get_checked_connection()
        changes = ResourceRecordSets(conn, hosted_zone_id, comment)

        if isinstance(names, basestring):
            names = [names]
        if isinstance(resource_records, basestring):
            resource_records = [resource_records]

        for name in names:
            # Assume there are not more than 10 WRRs for a given (name, type)
            rs = conn.get_all_rrsets(hosted_zone_id, type, name, maxitems=10)
            for record in rs:
                if record.name != name or record.type != type:
                    continue
                if record.identifier != identifier or record.weight != weight:
                    continue
                delete_record = changes.add_change(
                    "DELETE", name, type, record.ttl,
                    identifier=identifier, weight=weight)
                for value in record.resource_records:
                    delete_record.add_value(value)

            create_record = changes.add_change(
                "CREATE", name, type, ttl,
                identifier=identifier, weight=weight)
            for value in resource_records:
                create_record.add_value(value)

        return changes.commit()
