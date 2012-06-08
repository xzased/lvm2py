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

from ctypes import cast, c_ulonglong, c_ulong
import os
from conversion import *
from exception import *
from util import *
from pv import PhysicalVolume
from lv import LogicalVolume


class VolumeGroup(object):
    """
    *The VolumeGroup class is used as a wrapper to the global vg_t handle provided by
    the LVM api.*

    LVM works by providing a "handle" that represents each object instance (volume
    groups, logical and physical volumes). This class provides the "global" vg_t handle
    used to do volume group operations. You need to provide an LVM instance to instantiate
    this class::

        from lvm2py import *

        lvm = LVM()
        vg1 = lvm.get_vg("myexistingvg")

        # or just provide the LVM instance
        vg2 = VolumeGroup(lvm, "myexistingvg", mode="w")

    *Raises:*

    *       HandleError

    .. note::

        To create a new volume group use the LVM method create_vg.
    """
    def __init__(self, handle, name, mode="r"):
        self.__name = name
        self.__vgh = None
        self.__mode = mode
        self.__lvm = handle
        # verify we can open this vg in the desired mode
        handle.open()
        vgh = lvm_vg_open(handle.handle, name, mode)
        if not bool(vgh):
            raise HandleError("Failed to initialize VG Handle.")
        # Close the handle so we can proceed
        cl = lvm_vg_close(vgh)
        if cl != 0:
            raise HandleError("Failed to close VG handle after init check.")
        handle.close()

    def open(self):
        """
        Obtains the lvm and vg_t handle. Usually you would never need to use this method
        unless you are doing operations using the ctypes function wrappers in conversion.py

        *Raises:*

        *       HandleError
        """
        if not self.handle:
            self.lvm.open()
            self.__vgh = lvm_vg_open(self.lvm.handle, self.name, self.mode)
            if not bool(self.__vgh):
                raise HandleError("Failed to initialize VG Handle.")

    def close(self):
        """
        Closes the lvm and vg_t handle. Usually you would never need to use this method
        unless you are doing operations using the ctypes function wrappers in conversion.py

        *Raises:*

        *       HandleError
        """
        if self.handle:
            cl = lvm_vg_close(self.handle)
            if cl != 0:
                raise HandleError("Failed to close VG handle after init check.")
            self.__vgh = None
            self.lvm.close()

    @property
    def lvm(self):
        """
        Returns the LVM instance holding the lvm handle.
        """
        return self.__lvm

    @property
    def handle(self):
        """
        Returns the vg_t handle.
        """
        return self.__vgh

    @property
    def mode(self):
        """
        Returns the mode the instance is operating on ('r' or 'w').
        """
        return self.__mode

    @property
    def uuid(self):
        """
        Returns the volume group uuid.
        """
        self.open()
        uuid = lvm_vg_get_uuid(self.handle)
        self.close()
        return uuid

    @property
    def name(self):
        """
        returns the name of the volume group.
        """
        return self.__name

    @property
    def extent_count(self):
        """
        Returns the volume group extent count.
        """
        self.open()
        count = lvm_vg_get_extent_count(self.handle)
        self.close()
        return count

    @property
    def free_extent_count(self):
        """
        Returns the volume group free extent count.
        """
        self.open()
        count = lvm_vg_get_free_extent_count(self.handle)
        self.close()
        return count

    @property
    def pv_count(self):
        """
        Returns the physical volume count.
        """
        self.open()
        count = lvm_vg_get_pv_count(self.handle)
        self.close()
        return count

    @property
    def max_pv_count(self):
        """
        Returns the maximum allowed physical volume count.
        """
        self.open()
        count = lvm_vg_get_max_pv(self.handle)
        self.close()
        return count

    @property
    def max_lv_count(self):
        """
        Returns the maximum allowed logical volume count.
        """
        self.open()
        count = lvm_vg_get_max_lv(self.handle)
        self.close()
        return count

    @property
    def is_clustered(self):
        """
        Returns True if the VG is clustered, False otherwise.
        """
        self.open()
        clust = lvm_vg_is_clustered(self.handle)
        self.close()
        return bool(clust)

    @property
    def is_exported(self):
        """
        Returns True if the VG is exported, False otherwise.
        """
        self.open()
        exp = lvm_vg_is_exported(self.handle)
        self.close()
        return bool(exp)

    @property
    def is_partial(self):
        """
        Returns True if the VG is partial, False otherwise.
        """
        self.open()
        part = lvm_vg_is_partial(self.handle)
        self.close()
        return bool(part)

    @property
    def sequence(self):
        """
        Returns the volume group sequence number. This number increases
        everytime the volume group is modified.
        """
        self.open()
        seq = lvm_vg_get_seqno(self.handle)
        self.close()
        return seq

    def size(self, units="MiB"):
        """
        Returns the volume group size in the given units. Default units are  MiB.

        *Args:*

        *       units (str):    Unit label ('MiB', 'GiB', etc...). Default is MiB.
        """
        self.open()
        size = lvm_vg_get_size(self.handle)
        self.close()
        return size_convert(size, units)

    def free_size(self, units="MiB"):
        """
        Returns the volume group free size in the given units. Default units are  MiB.

        *Args:*

        *       units (str):    Unit label ('MiB', 'GiB', etc...). Default is MiB.
        """
        self.open()
        size = lvm_vg_get_free_size(self.handle)
        self.close()
        return size_convert(size, units)

    def extent_size(self, units="MiB"):
        """
        Returns the volume group extent size in the given units. Default units are  MiB.

        *Args:*

        *       units (str):    Unit label ('MiB', 'GiB', etc...). Default is MiB.
        """
        self.open()
        size = lvm_vg_get_extent_size(self.handle)
        self.close()
        return size_convert(size, units)

    def _commit(self):
        com = lvm_vg_write(self.handle)
        if com != 0:
            self.close()
            raise CommitError("Failed to commit changes to VolumeGroup.")

    def add_pv(self, device):
        """
        Initializes a device as a physical volume and adds it to the volume group::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.get_vg("myvg", "w")
            vg.add_pv("/dev/sdbX")

        *Args:*

        *       device (str):   An existing device.

        *Raises:*

        *       ValueError, CommitError, HandleError

       .. note::

            The VolumeGroup instance must be in write mode, otherwise CommitError
            is raised.
        """
        if not os.path.exists(device):
            raise ValueError("%s does not exist." % device)
        self.open()
        ext = lvm_vg_extend(self.handle, device)
        if ext != 0:
            self.close()
            raise CommitError("Failed to extend Volume Group.")
        self._commit()
        self.close()
        return PhysicalVolume(self, name=device)

    def get_pv(self, device):
        """
        Returns the physical volume associated with the given device::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.get_vg("myvg", "w")
            vg.get_pv("/dev/sdb1")

        *Args:*

        *       device (str):   An existing device.

        *Raises:*

        *       ValueError, HandleError
        """
        if not os.path.exists(device):
            raise ValueError("%s does not exist." % device)
        return PhysicalVolume(self, name=device)

    def get_lv(self, name):
        """
        Returns a LogicalVolume instance given an existin logical volume name::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.get_vg("myvg", "w")
            vg.get_lv("mylv")

        *Args:*

        *       name (str):   An existing logical volume name.

        *Raises:*

        *       HandleError
        """
        return LogicalVolume(self, name=name)

    def remove_pv(self, pv):
        """
        Removes a physical volume from the volume group::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.get_vg("myvg", "w")
            pv = vg.pvscan()[0]
            vg.remove_pv(pv)

        *Args:*

        *       pv (obj):       A PhysicalVolume instance.

        *Raises:*

        *       HandleError, CommitError

        .. note::

            The VolumeGroup instance must be in write mode, otherwise CommitError
            is raised. Also, when removing the last physical volume, the volume
            group is deleted in lvm, leaving the instance with a null handle.
        """
        name = pv.name
        self.open()
        rm = lvm_vg_reduce(self.handle, name)
        if rm != 0:
            self.close()
            raise CommitError("Failed to remove %s." % name)
        self._commit()
        self.close()

    def pvscan(self):
        """
        Probes the volume group for physical volumes and returns a list of
        PhysicalVolume instances::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.get_vg("myvg")
            pvs = vg.pvscan()

        *Raises:*

        *       HandleError
        """
        self.open()
        pv_list = []
        pv_handles = lvm_vg_list_pvs(self.handle)
        if not bool(pv_handles):
            return pv_list
        pvh = dm_list_first(pv_handles)
        while pvh:
            c = cast(pvh, POINTER(lvm_pv_list))
            pv = PhysicalVolume(self, pvh=c.contents.pv)
            pv_list.append(pv)
            if dm_list_end(pv_handles, pvh):
                # end of linked list
                break
            pvh = dm_list_next(pv_handles, pvh)
        self.close()
        return pv_list

    def lvscan(self):
        """
        Probes the volume group for logical volumes and returns a list of
        LogicalVolume instances::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.get_vg("myvg")
            lvs = vg.lvscan()

        *Raises:*

        *       HandleError
        """
        self.open()
        lv_list = []
        lv_handles = lvm_vg_list_lvs(self.handle)
        if not bool(lv_handles):
            return lv_list
        lvh = dm_list_first(lv_handles)
        while lvh:
            c = cast(lvh, POINTER(lvm_lv_list))
            lv = LogicalVolume(self, lvh=c.contents.lv)
            lv_list.append(lv)
            if dm_list_end(lv_handles, lvh):
                # end of linked list
                break
            lvh = dm_list_next(lv_handles, lvh)
        self.close()
        return lv_list

    def create_lv(self, name, length, units):
        """
        Creates a logical volume and returns the LogicalVolume instance associated with
        the lv_t handle::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.get_vg("myvg", "w")
            lv = vg.create_lv("mylv", 40, "MiB")

        *Args:*

        *       name (str):             The desired logical volume name.
        *       length (int):           The desired size.
        *       units (str):            The size units.

        *Raises:*

        *       HandleError,  CommitError, ValueError

        .. note::

            The VolumeGroup instance must be in write mode, otherwise CommitError
            is raised.
        """
        if units != "%":
            size = size_units[units] * length
        else:
            if not (0 < length <= 100) or type(length) is float:
                raise ValueError("Length not supported.")
            size = (self.size("B") / 100) * length
        self.open()
        lvh = lvm_vg_create_lv_linear(self.handle, name, c_ulonglong(size))
        if not bool(lvh):
            self.close()
            raise CommitError("Failed to create LV.")
        lv = LogicalVolume(self, lvh=lvh)
        self.close()
        return lv

    def remove_lv(self, lv):
        """
        Removes a logical volume from the volume group::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.get_vg("myvg", "w")
            lv = vg.lvscan()[0]
            vg.remove_lv(lv)

        *Args:*

        *       lv (obj):       A LogicalVolume instance.

        *Raises:*

        *       HandleError,  CommitError, ValueError

        .. note::

            The VolumeGroup instance must be in write mode, otherwise CommitError
            is raised.
        """
        lv.open()
        rm = lvm_vg_remove_lv(lv.handle)
        lv.close()
        if rm != 0:
            raise CommitError("Failed to remove LV.")

    def remove_all_lvs(self):
        """
        Removes all logical volumes from the volume group.

        *Raises:*

        *       HandleError,  CommitError
        """
        lvs = self.lvscan()
        for lv in lvs:
            self.remove_lv(lv)

    def set_mode(self, mode):
        """
        Sets the volume group in write or read mode.

        *Args:*

        *       mode (str):     'r' or 'w' for read/write respectively.
        """
        if mode != "r" and mode != "w":
            raise ValueError("Invalid mode.")
        self.__mode = mode

    def set_extent_size(self, length, units):
        """
        Sets the volume group extent size in the given units::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.get_vg("myvg", "w")
            vg.set_extent_size(2, "MiB")

        *Args:*

        *       length (int):   The desired length size.
        *       units (str):    The desired units ("MiB", "GiB", etc...).

        *Raises:*

        *       HandleError,  CommitError, KeyError

        .. note::

            The VolumeGroup instance must be in write mode, otherwise CommitError
            is raised.
        """
        size = length * size_units[units]
        self.open()
        ext = lvm_vg_set_extent_size(self.handle, c_ulong(size))
        self._commit()
        self.close()
        if ext != 0:
            raise CommitError("Failed to set extent size.")