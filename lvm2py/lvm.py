from collections import defaultdict
import weakref
from .conversion import *
from .exception import *
from .util import *
from .vg import VolumeGroup


class LVM(object):
    """
    *The LVM class is used as a wrapper to the global lvm handle provided by the api.*

    LVM works by providing a "handle" that represents each object instance (volume
    groups, logical and physical volumes). This class provides the "global" lvm handle
    used to access each of the above mentioned objects::

        from lvm2py import *

        lvm = LVM()

    Without arguments, the class uses the default system directory, you can override
    this by providing the path to the desired system directory::

        from lvm2py import *

        lvm = LVM("/my/system/dir")

    *Args:*

    *   path:   Alternative system directory.

    *Raises:*

    *   HandleError

    .. note::

       You can only create one instance of this class. Having multiple instances causes
       an error on lvm since it fails to provide a working "handle" raising a memory
       allocation problem. lvm2py keeps this from happening by raising a HandleError if
       a working handle is found.
    """
    __refs__ = defaultdict(list)

    def __init__(self, path=''):
        self.__refs__[self.__class__].append(weakref.ref(self))
        self.__handle = None
        self.__path = path
        inst = [i for i in self.get_instances()
                            if i.handle is not None]
        if len(inst) > 1:
            raise HandleError("Found existing LVM handle.")
        self.__handle = lvm_init(path)
        if not bool(self.__handle):
            raise HandleError("Failed to initialize LVM handle.")

    @classmethod
    def get_instances(cls):
        """
        Returns all instances of this class.
        """
        for ref in cls.__refs__[cls]:
            instance = ref()
            if instance is not None:
                yield instance

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
        Returns the lvm handle provided by the api represented by a ctypes opaque
        structure. After calling the close() method this will return None.
        """
        return self.__path

    @handleDecorator()
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

        *       name:   An existing volume group name.
        *       mode:   "r" or "w" for read/write respectively. Default is "r".

        *Raises:*

        *       HandleError
        """
        vg = VolumeGroup(self.handle, name=name, mode=mode)
        return vg

    @handleDecorator()
    def create_vg(self, name):
        """
        Returns a new instance of VolumeGroup with the given name. This volume group
        is only created in-memory. You must set parameters such as add physycal volumes
        to save ::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.get_vg("myvg")

        To open a volume group with write permissions set the mode parameter to "w"::

            from lvm2py import *

            lvm = LVM()
            vg = lvm.get_vg("myvg", "w")

        *Args:*

        *       name:   An existing volume group name.
        *       mode:   "r" or "w" for read/write respectively. Default is "r".

        *Raises:*

        *       HandleError
        """
        vgs, pvs, lvs = self._snapshot()
        if vgs:
            self._reset_handle()
            vg = VolumeGroup(self.handle, new=name)
            self._restore(vgs, pvs, lvs)
        else:
            vg = VolumeGroup(self.handle, new=name)
        return vg

    @handleDecorator()
    def remove_vg(self, vg):
        vgh = vg.handle
        rm = lvm_vg_remove(vgh)
        if rm != 0:
            raise CommitError("Failed to remove VG.")
        com = lvm_vg_write(vgh)
        if com != 0:
            raise CommitError("Failed to commit changes to disk.")

    @handleDecorator()
    def vgscan(self):
        lvm_scan(self.handle)
        vg_list = []
        vgnames = lvm_list_vg_names(self.handle)
        if dm_list_empty(vgnames):
            return vg_list
        vg = dm_list_first(vgnames)
        while vg:
            c = cast(vg, POINTER(lvm_str_list))
            vginst = self.get_vg(c.contents.str)
            vg_list.append(vginst)
            if dm_list_end(vgnames, vg):
                # end of linked list
                break
            vg = dm_list_next(vgnames, vg)
        return vg_list

    @handleDecorator()
    def close(self):
        vgs = [vg for vg in VolumeGroup.get_instances()]
        for vg in vgs:
            try:
                vg.close()
            except HandleError:
                # Probably a duplicate instance with an invalid handle
                pass
        q = lvm_quit(self.handle)
        if q != 0:
            raise HandleError("Failed to release LVM handle.")
        self.__handle = None

    def _snapshot(self):
        vgs = [(vg.name, vg.mode, vg) for vg in VolumeGroup.get_instances()
                                                if vg.handle is not None]
        pvs = {}
        for pv in PhysicalVolume.get_instances():
            if pv.handle is not None:
                try:
                    pvs[pv.vg_name] = pvs[pv.vg_name].append((pv.uuid, pv))
                except KeyError:
                    pvs[pv.vg_name] = [(pv.uuid, pv)]
        lvs = {}
        for lv in LogicalVolume.get_instances():
            if lv.handle is not None:
                try:
                    lvs[lv.vg_name] = lvs[lv.vg_name].append((lv.uuid, lv))
                except KeyError:
                    lvs[lv.vg_name] = [(lv.uuid, lv)]
        return vgs, pvs, lvs

    def _reset_handle(self):
        self.close()
        self.__handle = lvm_init(self.system_dir)
        if not bool(self.__handle):
            raise HandleError("Failed to initialize LVM handle.")

    def _restore(self, vgs, pvs, lvs):
        for name, mode, vg in vgs:
            vgh = lvm_vg_open(self.__handle, name, mode)
            vg._VolumeGroup__vgh = vgh
            pvinst = pvs.get(name, [])
            for uuid, pv in pvinst:
                pvh = lvm_pv_from_uuid(vgh, uuid)
                pv._PhysicalVolume__pvh = pvh
            lvinst = lvs.get(name, [])
            for uuid, lv in lvinst:
                lvh = lvm_lv_from_uuid(vgh, uuid)
                lv._LogicalVolume__lvh = lvh