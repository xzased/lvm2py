from .conversion import *
from .exception import *
from .util import *
from collections import defaultdict
import weakref

# Physical volume handling should not be needed anymore. Only physical volumes
# bound to a vg contain useful information. Therefore the creation,
# modification and the removal of orphan physical volumes is not suported.


class PhysicalVolume(object):
    __refs__ = defaultdict(list)

    def __init__(self, pvh, vg, uuid=None):
        self.__refs__[self.__class__].append(weakref.ref(self))
        self.__pvh = pvh
        self.__vg = vg
        if not bool(self.__pvh):
            raise HandleError("Failed to initialize PV Handle.")

    @classmethod
    def get_instances(cls):
        for ref in cls.__refs__[cls]:
            instance = ref()
            if instance is not None:
                yield instance

    @property
    def handle(self):
        return self.__pvh

    @property
    def vg_name(self):
        return self.__vg

    @property
    @handleDecorator()
    def name(self):
        name = lvm_pv_get_name(self.handle)
        return name

    @property
    @handleDecorator()
    def uuid(self):
        uuid = lvm_pv_get_uuid(self.handle)
        return uuid

    @property
    @handleDecorator()
    def mda_count(self):
        mda = lvm_pv_get_mda_count(self.handle)
        return mda

    @handleDecorator()
    def size(self, units="MB"):
        size = lvm_pv_get_size(self.handle)
        return size_convert(size, units)

    @handleDecorator()
    def dev_size(self, units="MB"):
        size = lvm_pv_get_dev_size(self.handle)
        return size_convert(size, units)

    @handleDecorator()
    def free(self, units="MB"):
        size = lvm_pv_get_free(self.handle)
        return size_convert(size, units)