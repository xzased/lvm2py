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
from conversion import *
from exception import *
from util import *
from vg import VolumeGroup
import os


class LVM(object):
    """
    *The LVM class is used as a wrapper to the global lvm handle provided by the api.*

    LVM works by providing a "handle" that represents each object instance (volume
    groups, logical and physical volumes). This class provides the "global" lvm handle
    used to access each of the above mentioned objects::

        from lvm2py import *

        lvm = LVM()
    """
    def __init__(self):
        self.__handle = None
        self.__path = None

    @classmethod
    def set_system_dir(self, path):
        """
        This class method overrides the default system directory::

            from lvm2py import *

            lvm = LVM()
            lvm.set_system_dir("/path/to/dir")

        .. note::

            LVM probes the environment variable LVM_SYSTEM_DIR, if this is not set
            it will use the default directory (usually /etc/lvm/) .
        """
        self.__path = path

    def open(self):
        """
        Obtains the lvm handle. Usually you would never need to use this method unless
        you are trying to do operations using the ctypes function wrappers in conversion.py

        *Raises:*

        *       HandleError
        """
        if not self.handle:
            try:
                path = self.system_dir
            except AttributeError:
                path = ''
            self.__handle = lvm_init(path)
            if not bool(self.__handle):
                raise HandleError("Failed to initialize LVM handle.")

    def close(self):
        """
        Closes the lvm handle. Usually you would never need to use this method unless
        you are trying to do operations using the ctypes function wrappers in conversion.py

        *Raises:*

        *       HandleError
        """
        if self.handle:
            q = lvm_quit(self.handle)
            if q != 0:
                raise HandleError("Failed to close LVM handle.")
            self.__handle = None

    def _close_vg(self, vgh):
        cl = lvm_vg_close(vgh)
        if cl != 0:
            raise HandleError("Failed to close VG handle.")
        self.close()

    def _commit_vg(self, vgh):
        com = lvm_vg_write(vgh)
        if com != 0:
            raise CommitError("Failed to add VolumeGroup.")

    def _destroy_vg(self, vgh):
        rm = lvm_vg_remove(vgh)
        if rm == 0:
            self._commit_vg(vgh)
        self._close_vg(vgh)

    @property
    def handle(self):
        """
        Returns the lvm handle provided by the api represented by a ctypes opaque
        structure. After calling the close() method this will return None.
        """
        return self.__handle

    @property
    def system_dir(self):
        """
        Returns the lvm system directory. Returns None if you have not set it using
        the set_system_dir method.
        """
        return self.__path

    @property
    def lvm_version(self):
        """
        Returns the lvm library version.
        """
        return version()

    def get_vg(self, name, mode="r"):
        """
        Returns an instance of VolumeGroup. The name parameter should be an existing
        volume group. By default, all volume groups are open in "read" mode::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.get_vg("myvg")

        To open a volume group with write permissions set the mode parameter to "w"::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.get_vg("myvg", "w")

        *Args:*

        *       name (str):     An existing volume group name.
        *       mode (str):     "r" or "w" for read/write respectively. Default is "r".

        *Raises:*

        *       HandleError
        """
        vg = VolumeGroup(self, name=name, mode=mode)
        return vg

    def create_vg(self, name, devices):
        """
        Returns a new instance of VolumeGroup with the given name and added physycal
        volumes (devices)::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.create_vg("myvg", ["/dev/sdb1", "/dev/sdb2"])

        *Args:*

        *       name (str):             A volume group name.
        *       devices (list):         A list of device paths.

        *Raises:*

        *       HandleError, CommitError, ValueError
        """
        self.open()
        vgh = lvm_vg_create(self.handle, name)
        if not bool(vgh):
            self.close()
            raise HandleError("Failed to create VG.")
        for device in devices:
            if not os.path.exists(device):
                self._destroy_vg(vgh)
                raise ValueError("%s does not exist." % device)
            ext = lvm_vg_extend(vgh, device)
            if ext != 0:
                self._destroy_vg(vgh)
                raise CommitError("Failed to extend Volume Group.")
            try:
                self._commit_vg(vgh)
            except CommitError:
                self._destroy_vg(vgh)
                raise CommitError("Failed to add %s to VolumeGroup." % device)
        self._close_vg(vgh)
        vg = VolumeGroup(self, name)
        return vg

    def remove_vg(self, vg):
        """
        Removes a volume group::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.get_vg("myvg", "w")
            lvm.remove_vg(vg)

        *Args:*

        *       vg (obj):       A VolumeGroup instance.

        *Raises:*

        *       HandleError,  CommitError

        .. note::

            The VolumeGroup instance must be in write mode, otherwise CommitError
            is raised.
        """
        vg.open()
        rm = lvm_vg_remove(vg.handle)
        if rm != 0:
            vg.close()
            raise CommitError("Failed to remove VG.")
        com = lvm_vg_write(vg.handle)
        if com != 0:
            vg.close()
            raise CommitError("Failed to commit changes to disk.")
        vg.close()

    def vgscan(self):
        """
        Probes the system for volume groups and returns a list of VolumeGroup
        instances::

            from lvm2py import *

            lvm = LVM()
            vgs = lvm.vgscan()

        *Raises:*

        *       HandleError
        """
        vg_list = []
        self.open()
        names = lvm_list_vg_names(self.handle)
        if not bool(names):
            return vg_list
        vgnames = []
        vg = dm_list_first(names)
        while vg:
            c = cast(vg, POINTER(lvm_str_list))
            vgnames.append(c.contents.str)
            if dm_list_end(names, vg):
                # end of linked list
                break
            vg = dm_list_next(names, vg)
        self.close()
        for name in vgnames:
            vginst = self.get_vg(name)
            vg_list.append(vginst)
        return vg_list