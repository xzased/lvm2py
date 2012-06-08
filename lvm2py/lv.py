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
from util import *


class LogicalVolume(object):
    """
    *The LogicalVolume class is used as a wrapper to the global lv_t handle provided by
    the LVM api.*

    LVM works by providing a "handle" that represents each object instance (volume
    groups, logical and physical volumes). This class provides the "global" lv_t handle
    used to do logical volume operations. You need to provide an VolumeGroup instance to
    instantiate this class::

        from lvm2py import *

        lvm = LVM()
        vg = lvm.get_vg("myexistingvg")
        # get pv from pvscan
        lv1 = vg.lvscan()[0]
        # get it by name
        lv2 = vg.get_lv("mylv")
        # or just instantiate it
        lv3 = LogicalVolume(vg, name="mylv")

    *Raises:*

    *       HandleError

    .. note::

        To create a new logical volume use the VolumeGroup method create_lv.
    """
    def __init__(self, vg, lvh=None, name=None):
        self.__vg = vg
        if name:
            self.__vg.open()
            self.__lvh = lvm_lv_from_name(vg.handle, name)
            if not bool(self.__lvh):
                raise HandleError("Failed to initialize LV Handle.")
            self.__uuid = lvm_lv_get_uuid(self.__lvh)
            self.__vg.close()
        else:
            self.__lvh = lvh
            if not bool(self.__lvh):
                raise HandleError("Failed to initialize LV Handle.")
            self.__uuid = lvm_lv_get_uuid(self.__lvh)

    def open(self):
        """
        Obtains the lvm, vg_t and lv_t handle. Usually you would never need to use this
        method unless you are doing operations using the ctypes function wrappers in
        conversion.py

        *Raises:*

        *       HandleError
        """
        self.vg.open()
        self.__lvh = lvm_lv_from_uuid(self.vg.handle, self.uuid)
        if not bool(self.__lvh):
            raise HandleError("Failed to initialize LV Handle.")

    def close(self):
        """
        Closes the lvm, vg_t and lv_t handle. Usually you would never need to use this
        method unless you are doing operations using the ctypes function wrappers in
        conversion.py

        *Raises:*

        *       HandleError
        """
        self.vg.close()

    @property
    def handle(self):
        """
        Returns the lv_t handle.
        """
        return self.__lvh

    @property
    def vg(self):
        """
        Returns the VG instance holding the lvm and vg_t handle.
        """
        return self.__vg

    @property
    def name(self):
        """
        Returns the logical volume name.
        """
        self.open()
        name = lvm_lv_get_name(self.__lvh)
        self.close()
        return name

    @property
    def uuid(self):
        """
        Returns the logical volume uuid.
        """
        return self.__uuid

    @property
    def is_active(self):
        """
        Returns True if the logical volume is active, False otherwise.
        """
        self.open()
        active = lvm_lv_is_active(self.__lvh)
        self.close()
        return bool(active)

    @property
    def is_suspended(self):
        """
        Returns True if the logical volume is suspended, False otherwise.
        """
        self.open()
        susp = lvm_lv_is_suspended(self.__lvh)
        self.close()
        return bool(susp)

    def size(self, units="MiB"):
        """
        Returns the logical volume size in the given units. Default units are  MiB.

        *Args:*

        *       units (str):    Unit label ('MiB', 'GiB', etc...). Default is MiB.
        """
        self.open()
        size = lvm_lv_get_size(self.__lvh)
        self.close()
        return size_convert(size, units)

    def activate(self):
        """
        Activates the logical volume.

        *Raises:*

        *       HandleError
        """
        self.open()
        a = lvm_lv_activate(self.handle)
        self.close()
        if a != 0:
            raise CommitError("Failed to activate LV.")

    def deactivate(self):
        """
        Deactivates the logical volume.

        *Raises:*

        *       HandleError
        """
        self.open()
        d = lvm_lv_deactivate(self.handle)
        self.close()
        if d != 0:
            raise CommitError("Failed to deactivate LV.")