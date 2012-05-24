#This file is part of lvm2py.

#lvm2py is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#lvm2py is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with lvm2py. If not, see <http://www.gnu.org/licenses/>.
from ctypes import cast, c_ulonglong
from collections import defaultdict
import weakref, os
from .conversion import *
from .exception import *
from .util import *
from .pv import PhysicalVolume
from .lv import LogicalVolume


class VolumeGroup(object):
    __refs__ = defaultdict(list)

    def __init__(self, handle, new=None, name=None, mode="r", device=None):
        self.__refs__[self.__class__].append(weakref.ref(self))
        self.__name = None
        self.__vgh = None
        self.__handle = handle
        if new:
            self.__name = new
            self.__vgh = lvm_vg_create(handle, new)
        elif name:
            self.__vgh = lvm_vg_open(handle, name, mode)
            self.__name = name
        elif device:
            if not os.path.exists(device):
                raise ValueError("%s does not exist." % device)
            name = lvm_vgname_from_device(handle, device)
            if not name:
                raise HandleError("Could not find Volume Group.")
            self.__vgh = lvm_vg_open(handle, name, mode)
            self.__name = name
        if not bool(self.__vgh):
            raise HandleError("Failed to initialize VG Handle.")

    @classmethod
    def get_instances(cls):
        for ref in cls.__refs__[cls]:
            instance = ref()
            if instance is not None:
                yield instance

    @property
    def handle(self):
        return self.__vgh

    @property
    @handleDecorator()
    def uuid(self):
        uuid = lvm_vg_get_uuid(self.handle)
        return uuid

    @property
    @handleDecorator()
    def name(self):
        if not self.__name:
            self.__name = lvm_vg_get_name(self.handle)
        return self.__name

    @property
    @handleDecorator()
    def extent_count(self):
        count = lvm_vg_get_extent_count(self.handle)
        return count

    @property
    @handleDecorator()
    def free_extent_count(self):
        count = lvm_vg_get_free_extent_count(self.handle)
        return count

    @property
    @handleDecorator()
    def pv_count(self):
        count = lvm_vg_get_pv_count(self.handle)
        return count

    @property
    @handleDecorator()
    def max_pv_count(self):
        count = lvm_vg_get_max_pv(self.handle)
        return count

    @property
    @handleDecorator()
    def max_lv_count(self):
        count = lvm_vg_get_max_lv(self.handle)
        return count

    @property
    @handleDecorator()
    def is_clustered(self):
        clust = lvm_vg_is_clustered(self.handle)
        return bool(clust)

    @property
    @handleDecorator()
    def is_exported(self):
        exp = lvm_vg_is_exported(self.handle)
        return bool(exp)

    @property
    @handleDecorator()
    def is_partial(self):
        part = lvm_vg_is_partial(self.handle)
        return bool(part)

    @property
    @handleDecorator()
    def sequence(self):
        seq = lvm_vg_get_seqno(self.handle)
        return seq

    @handleDecorator()
    def size(self, units="MB"):
        size = lvm_vg_get_size(self.handle)
        return size_convert(size, units)

    @handleDecorator()
    def free_size(self, units="MB"):
        size = lvm_vg_get_free_size(self.handle)
        return size_convert(size, units)

    @handleDecorator()
    def extent_size(self, units="MB"):
        size = lvm_vg_get_extent_size(self.handle)
        return size_convert(size, units)

    @handleDecorator()
    def close(self):
        lvs = [lv for lv in LogicalVolume.get_instances()]
        pvs = [pv for pv in PhysicalVolume.get_instances()]
        cl = lvm_vg_close(self.handle)
        if cl != 0:
            raise CloseError("Failed to close Volume Group handle.")
        self.__vgh = None
        for lv in lvs:
            lv._LogicalVolume__lvh = None
        for pv in pvs:
            pv._PhysicalVolume__pvh = None

    @handleDecorator()
    def commit(self):
        com = lvm_vg_write(self.handle)
        if com != 0:
            raise CommitError("Failed to commit changes to VolumeGroup.")

    @handleDecorator()
    def add_pv(self, device):
        if not os.path.exists(device):
            raise ValueError("%s does not exist." % device)
        ext = lvm_vg_extend(self.handle, device)
        if ext != 0:
            raise VolumeGroupError("Failed to extend Volume Group.")

    @handleDecorator()
    def remove_pv(self, pv):
        rm = lvm_vg_reduce(self.handle, pv.name)
        if rm != 0:
            raise VolumeGroupError("Failed to remove %s." % device)
        pv.__pvh = None

    @handleDecorator()
    def pvscan(self):
        pv_list = []
        pv_handles = lvm_vg_list_pvs(self.handle)
        if dm_list_empty(pv_handles):
            return pv_list
        pvh = pv_handles.contents.n
        while pvh:
            c = cast(pvh, POINTER(lvm_pv_list))
            pv = PhysicalVolume(c.contents.pv)
            pv_list.append(pv)
            if dm_list_end(pv_handles, pvh):
                # end of linked list
                break
            pvh = pvh.contents.n
        return pv_list

    @handleDecorator()
    def lvscan(self):
        lv_list = []
        lv_handles = lvm_vg_list_lvs(self.handle)
        if dm_list_empty(lv_handles):
            return lv_list
        lvh = lv_handles.contents.n
        while lvh:
            c = cast(lvh, POINTER(lvm_lv_list))
            lv = LogicalVolume(c.contents.lv)
            lv_list.append(lv)
            if dm_list_end(lv_handles, lvh):
                # end of linked list
                break
            lvh = lvh.contents.n
        return lv_list

    @handleDecorator()
    def create_lv(self, name, length, units):
        if units != "%":
            size = size_units[units] * length
        else:
            if not (0 < length <= 100) or type(length) is float:
                raise ValueError("Length not supported.")
            size = (self.size("B") / 100) * length
        lvh = lvm_vg_create_lv_linear(self.handle, name, c_ulonglong(size))
        if not bool(lvh):
            raise CommitError("Failed to create LV.")
        lv = LogicalVolume(lvh)
        return lv

    @handleDecorator()
    def remove_lv(self, lv):
        lvh = lv.handle
        rm = lvm_vg_remove_lv(lvh)
        if rm != 0:
            raise CommitError("Failed to remove LV.")
        lv.__lvh = None

    def remove_all_lvs(self):
        lvs = self.lvscan()
        for lv in lvs:
            self.remove_lv(lv)

    @handleDecorator()
    def set_mode(self, mode):
        if mode != "r" and mode != "w":
            raise ValueError("Invalid mode.")
        self.__vgh = lvm_vg_open(self.__handle, self.name, mode)

    @handleDecorator()
    def set_extent_size(self, length, units):
        size = length * size_units[units]
        ext = lvm_vg_set_extent_size(self.handle, c_ulong(size))
        if ext != 0:
            raise VolumeGroupError("Failed to set extent size.")