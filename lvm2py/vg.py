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

from conversion import *
from exception import *
from pv import PhysicalVolume
from ctypes import cast
from . import handle
import os

class VolumeGroup(object):
    def __init__(self, new=None, name=None, mode="r", device=None):
        self.__name = None
        self.__vgh = None
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
        if not type(self.__vgh) == vg_t:
            raise HandleError("Failed to initialize VG Handle.")

    @property
    def uuid(self):
        uuid = lvm_vg_get_uuid(self.__vgh)
        return uuid

    @property
    def name(self):
        if not self.__name:
            self.__name = lvm_vg_get_name(self.__vgh)
        return self.__name

    @property
    def size(self):
        sz = lvm_vg_get_size(self.__vgh)
        return sz

    @property
    def free_size(self):
        sz = lvm_vg_get_free_size(self.__vgh)
        return sz

    @property
    def extent_size(self):
        sz = lvm_vg_get_extent_size(self.__vgh)
        return sz

    @property
    def extent_count(self):
        count = lvm_vg_get_extent_count(self.__vgh)
        return count

    @property
    def free_extent_count(self):
        count = lvm_vg_get_free_extent_count(self.__vgh)
        return count

    @property
    def pv_count(self):
        count = lvm_vg_get_pv_count(self.__vgh)
        return count

    @property
    def max_pv_count(self):
        count = lvm_vg_get_max_pv(self.__vgh)
        return count

    @property
    def max_lv_count(self):
        count = lvm_vg_get_max_lv(self.__vgh)
        return count

    def close(self):
        cl = lvm_vg_close(self.__vgh)
        if cl != 0:
            raise CloseError("Failed to close Volume Group handle.")

    def commit(self):
        com = lvm_vg_write(self.__vgh)
        if com != 0:
            raise CommitError("Failed to commit changes to VolumeGroup.")

    def add_pv(self, device):
        if not os.path.exists(device):
            raise ValueError("%s does not exist.")
        ext = lvm_vg_extend(self.__vgh, device)
        if ext != 0:
            raise VolumeGroupError("Failed to extend Volume Group.")

    def pv_list(self):
        pv_list = []
        pv_handles = lvm_vg_list_pvs(self.__vgh)
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