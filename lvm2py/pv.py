from .conversion import *
from .exception import *


# Physical volume handling should not be needed anymore. Only physical volumes
# bound to a vg contain useful information. Therefore the creation,
# modification and the removal of orphan physical volumes is not suported.


class PhysicalVolume(object):
    def __init__(self, pvh):
        self.__pvh = pvh
        if not type(self.__pvh) == pv_t:
            raise HandleError("Failed to initialize PV Handle.")

    @property
    def name(self):
        name = lvm_pv_get_name(self.__pvh)
        return name

    @property
    def uuid(self):
        uuid = lvm_pv_get_uuid(self.__pvh)
        return uuid

    @property
    def mda_count(self):
        mda = lvm_pv_get_mda_count(self.__pvh)
        return mda

    @property
    def size(self):
        size = lvm_pv_get_size(self.__pvh)
        return size

    @property
    def dev_size(self):
        size = lvm_pv_get_dev_size(self.__pvh)
        return size

    @property
    def free(self):
        free = lvm_pv_get_free(self.__pvh)
        return free