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

from .conversion import *
from .exception import *
from .pv import PhysicalVolume
from .lv import LogicalVolume
from ctypes import cast, c_ulonglong
import os

class VolumeGroup(object):
    def __init__(self, handle, name=None, mode="r", device=None):
        self.__name = None
        self.__vgh = None
        #if new:
            #self.__name = new
            #self.__vgh = lvm_vg_create(handle, new)
        if name:
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

    @property
    def handle(self):
        return self.__vgh

    @property
    def uuid(self):
        uuid = lvm_vg_get_uuid(self.handle)
        return uuid

    @property
    def name(self):
        if not self.__name:
            self.__name = lvm_vg_get_name(self.handle)
        return self.__name

    @property
    def size(self):
        sz = lvm_vg_get_size(self.handle)
        return sz

    @property
    def free_size(self):
        sz = lvm_vg_get_free_size(self.handle)
        return sz

    @property
    def extent_size(self):
        sz = lvm_vg_get_extent_size(self.handle)
        return sz

    @property
    def extent_count(self):
        count = lvm_vg_get_extent_count(self.handle)
        return count

    @property
    def free_extent_count(self):
        count = lvm_vg_get_free_extent_count(self.handle)
        return count

    @property
    def pv_count(self):
        count = lvm_vg_get_pv_count(self.handle)
        return count

    @property
    def max_pv_count(self):
        count = lvm_vg_get_max_pv(self.handle)
        return count

    @property
    def max_lv_count(self):
        count = lvm_vg_get_max_lv(self.handle)
        return count

    def close(self):
        cl = lvm_vg_close(self.handle)
        if cl != 0:
            raise CloseError("Failed to close Volume Group handle.")

    def commit(self):
        com = lvm_vg_write(self.handle)
        if com != 0:
            raise CommitError("Failed to commit changes to VolumeGroup.")

    def add_pv(self, device):
        if not os.path.exists(device):
            raise ValueError("%s does not exist." % device)
        ext = lvm_vg_extend(self.handle, device)
        if ext != 0:
            raise VolumeGroupError("Failed to extend Volume Group.")

    def remove_pv(self, device):
        if not os.path.exists(device):
            raise ValueError("%s does not exist." % device)
        ext = lvm_vg_reduce(self.handle, device)
        if ext != 0:
            raise VolumeGroupError("Failed to remove %s." % device)

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

    def create_lv(self, name, size):
        lvh = lvm_vg_create_lv_linear(self.handle, name, c_ulonglong(size))
        if not bool(lvh):
            raise CommitError("Failed to create LV.")
        lv = LogicalVolume(lvh)
        return lv

    def remove_lv(self, lv):
        lvh = lv.handle
        rm = lvm_vg_remove_lv(lvh)
        if rm != 0:
            raise CommitError("Failed to remove LV.")

    def remove_all_lvs(self):
        lvs = self.lvscan()
        for lv in lvs:
            self.remove_lv(lv)