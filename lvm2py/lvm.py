from collections import defaultdict
import weakref
from .conversion import *
from .exception import *
from .util import *
from .vg import VolumeGroup


class LVM(object):
    __refs__ = defaultdict(list)

    def __init__(self, path=''):
        self.__refs__[self.__class__].append(weakref.ref(self))
        self.__handle = None
        inst = [i for i in self.get_instances()
                            if i.handle is not None]
        if len(inst) > 1:
            raise HandleError("Found existing LVM handle.")
        self.__handle = lvm_init(path)
        if not bool(self.__handle):
            raise HandleError("Failed to initialize LVM handle.")

    @classmethod
    def get_instances(cls):
        for ref in cls.__refs__[cls]:
            instance = ref()
            if instance is not None:
                yield instance

    @property
    def handle(self):
        return self.__handle

    @handleDecorator()
    def get_vg(self, name, mode="r"):
        vg = VolumeGroup(self.handle, name=name, mode=mode)
        return vg

    @handleDecorator()
    def create_vg(self, name):
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
        vg = vgnames.contents.n
        while vg:
            c = cast(vg, POINTER(lvm_str_list))
            vginst = VolumeGroup(self.handle, name=c.contents.str)
            vg_list.append(vginst)
            if dm_list_end(vgnames, vg):
                # end of linked list
                break
            vg = vg.contents.n
        return vg_list

    @handleDecorator()
    def close(self):
        vgs = [vg for vg in VolumeGroup.get_instances()]
        for vg in vgs:
            vg.close()
        q = lvm_quit(self.handle)
        if q != 0:
            raise HandleError("Failed to release LVM handle.")
        self.__handle = None