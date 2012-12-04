# -*- coding: utf-8 -*-

from sqlalchemy import (
    Table,
    Column,
    Integer,
    Boolean,
    Text,
    UnicodeText,
    ForeignKey,
    )
from sqlalchemy.orm import (
    relationship,
    backref,
    )

from .meta import BaseModel

__all__ = ['InstanceModel', 'VolumeModel']


class InstanceModel(BaseModel):
    __tablename__ = 'instances'

    id = Column(Integer, primary_key=True)
    instance_id = Column(Text, nullable=False)
    instance_type = Column(Text, nullable=False)
    name = Column(UnicodeText, default=u"")
    arch = Column(Text, default="")
    platform = Column(Text, default="")
    region = Column(Text, nullable=False)
    placement = Column(Text, nullable=False)
    is_obsolete = Column(Boolean, nullable=False, default=False)
    hostnames = Column(Text, default="")
    volumes = relationship("VolumeModel", backref="instance")

    def get_current_volumes(self):
        return [volume for volume in self.volumes if not volume.is_obsolete]

    @classmethod
    def update_cache(cls, cached_instance, instance):
        if cached_instance is None:
            cached_instance = cls(instance_id=instance.id)
        cached_instance.name = instance.tags.get("Name", "")
        cached_instance.instance_type = instance.instance_type
        cached_instance.arch = instance.architecture
        cached_instance.platform = instance.platform
        cached_instance.region = instance.region.name
        cached_instance.placement = instance.placement
        return cached_instance


class VolumeModel(BaseModel):
    __tablename__ = 'volumes'

    id = Column(Integer, primary_key=True)
    volume_id = Column(Text, nullable=False)
    name = Column(UnicodeText, default=u"")
    size = Column(Integer)
    region = Column(Text, nullable=False)
    placement = Column(Text, nullable=False)
    instance_id = Column(Integer, ForeignKey('instances.id'))
    is_obsolete = Column(Boolean, nullable=False, default=False)

    @classmethod
    def update_cache(cls, cached_volume, volume):
        from boto.ec2.volume import Volume
        assert isinstance(volume, Volume)
        if cached_volume is None:
            cached_volume = cls(volume_id=volume.id)
        cached_volume.name = volume.tags.get("Name", "")
        cached_volume.size = volume.size
        cached_volume.region = volume.region.name
        cached_volume.placement = volume.zone
        return cached_volume
