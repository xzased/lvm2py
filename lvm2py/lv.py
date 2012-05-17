from .conversion import *
from .exception import *


class LogicalVolume(object):
    def __init__(self, lvh, name=None):
        self.__lvh = lvh
        if not bool(self.__lvh):
            raise HandleError("Failed to initialize LV Handle.")

    @property
    def handle(self):
        return self.__lvh

    @property
    def name(self):
        name = lvm_lv_get_name(self.__lvh)
        return name

    @property
    def uuid(self):
        uuid = lvm_lv_get_uuid(self.__lvh)
        return uuid

    @property
    def size(self):
        size = lvm_lv_get_size(self.__lvh)
        return size