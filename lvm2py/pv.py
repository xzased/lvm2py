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
from .util import *

# Physical volume handling should not be needed anymore. Only physical volumes
# bound to a vg contain useful information. Therefore the creation,
# modification and the removal of orphan physical volumes is not suported.


class PhysicalVolume(object):
    """
    *The PhysicalVolume class is used as a wrapper to the global pv_t handle provided by
    the LVM api.*

    LVM works by providing a "handle" that represents each object instance (volume
    groups, logical and physical volumes). This class provides the "global" pv_t handle
    used to do physical volume operations. You need to provide an VolumeGroup instance to
    instantiate this class::

        from lvm2py import *

        lvm = LVM()
        vg = lvm.get_vg("myexistingvg")
        # get pv from pvscan
        pv1 = vg.pvscan()[0]
        # get it by name
        pv2 = vg.get_pv("/dev/sdb1")
        # or just instantiate it
        pv3 = PhysicalVolume(vg, name="/dev/sdb1")

    *Raises:*

    *       HandleError

    .. note::

        To add a new physical volume use the VolumeGroup method add_pv.
    """
    def __init__(self, vg, pvh=None, name=None):
        self.__vg = vg
        if name:
            self.__vg.open()
            self.__pvh = lvm_pv_from_name(vg.handle, name)
            if not bool(self.__pvh):
                raise HandleError("Failed to initialize PV Handle.")
            self.__uuid = lvm_pv_get_uuid(self.__pvh)
            self.__vg.close()
        else:
            self.__pvh = pvh
            if not bool(self.__pvh):
                raise HandleError("Failed to initialize PV Handle.")
            self.__uuid = lvm_pv_get_uuid(self.__pvh)

    def open(self):
        """
        Obtains the lvm, vg_t and pv_t handle. Usually you would never need to use this
        method unless you are doing operations using the ctypes function wrappers in
        conversion.py

        *Raises:*

        *       HandleError
        """
        self.vg.open()
        self.__pvh = lvm_pv_from_uuid(self.vg.handle, self.uuid)
        if not bool(self.__pvh):
            raise HandleError("Failed to initialize PV Handle.")

    def close(self):
        """
        Closes the lvm, vg_t and pv_t handle. Usually you would never need to use this
        method unless you are doing operations using the ctypes function wrappers in
        conversion.py

        *Raises:*

        *       HandleError
        """
        self.vg.close()

    @property
    def handle(self):
        """
        Returns the pv_t handle.
        """
        return self.__pvh

    @property
    def vg(self):
        """
        Returns the VG instance holding the lvm and vg_t handle.
        """
        return self.__vg

    @property
    def name(self):
        """
        Returns the physical volume device path.
        """
        self.open()
        name = lvm_pv_get_name(self.handle)
        self.close()
        return name

    @property
    def uuid(self):
        """
        Returns the physical volume uuid.
        """
        return self.__uuid

    @property
    def mda_count(self):
        """
        Returns the physical volume mda count.
        """
        self.open()
        mda = lvm_pv_get_mda_count(self.handle)
        self.close()
        return mda

    def size(self, units="MiB"):
        """
        Returns the physical volume size in the given units. Default units are  MiB.

        *Args:*

        *       units (str):    Unit label ('MiB', 'GiB', etc...). Default is MiB.
        """
        self.open()
        size = lvm_pv_get_size(self.handle)
        self.close()
        return size_convert(size, units)

    def dev_size(self, units="MiB"):
        """
        Returns the device size in the given units. Default units are  MiB.

        *Args:*

        *       units (str):    Unit label ('MiB', 'GiB', etc...). Default is MiB.
        """
        self.open()
        size = lvm_pv_get_dev_size(self.handle)
        self.close()
        return size_convert(size, units)

    def free(self, units="MiB"):
        """
        Returns the free size in the given units. Default units are  MiB.

        *Args:*

        *       units (str):    Unit label ('MiB', 'GiB', etc...). Default is MiB.
        """
        self.open()
        size = lvm_pv_get_free(self.handle)
        self.close()
        return size_convert(size, units)
