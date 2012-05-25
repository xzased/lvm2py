from .conversion import *
from .exception import *
from .util import *
from collections import defaultdict
import weakref


class LogicalVolume(object):
    __refs__ = defaultdict(list)

    def __init__(self, lvh, vg, uuid=None):
        self.__refs__[self.__class__].append(weakref.ref(self))
        self.__lvh = lvh
        self.__vg = vg
        if not bool(self.__lvh):
            raise HandleError("Failed to initialize LV Handle.")

    @classmethod
    def get_instances(cls):
        for ref in cls.__refs__[cls]:
            instance = ref()
            if instance is not None:
                yield instance

    @property
    def handle(self):
        return self.__lvh

    @property
    def vg_name(self):
        return self.__vg

    @property
    @handleDecorator()
    def name(self):
        name = lvm_lv_get_name(self.__lvh)
        return name

    @property
    @handleDecorator()
    def uuid(self):
        uuid = lvm_lv_get_uuid(self.__lvh)
        return uuid

    @property
    @handleDecorator()
    def is_active(self):
        active = lvm_lv_is_active(self.__lvh)
        return bool(active)

    @property
    @handleDecorator()
    def is_suspended(self):
        susp = lvm_lv_is_suspended(self.__lvh)
        return bool(susp)

    @handleDecorator()
    def size(self, units="MB"):
        size = lvm_lv_get_size(self.__lvh)
        return size_convert(size, units)

    @handleDecorator()
    def activate(self):
        a = lvm_lv_activate(self.handle)
        if a != 0:
            raise LogicalVolumeError("Failed to activate LV.")

    @handleDecorator()
    def deactivate(self):
        d = lvm_lv_deactivate(self.handle)
        if d != 0:
            raise LogicalVolumeError("Failed to deactivate LV.")