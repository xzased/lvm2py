from .conversion import *
from .exception import *
from .vg import VolumeGroup

class LVM(object):
    def __init__(self, path=''):
        self.__handle = lvm_init(path)
        if not bool(self.__handle):
            raise HandleError("Failed to initialize LVM handle.")

    @property
    def handle(self):
        return self.__handle

    def get_vg(self, name, mode="r"):
        vg = VolumeGroup(self.handle, name=name, mode=mode)
        return vg

    def create_vg(self, name):
        vg = VolumeGroup(self.handle, new=name)
        return vg

    def remove_vg(self, vg):
        vgh = vg.handle
        rm = lvm_vg_remove(vgh)
        if rm != 0:
            raise CommitError("Failed to remove VG.")
        com = lvm_vg_write(vgh)
        if com != 0:
            raise CommitError("Failed to commit changes to disk.")

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

    def close(self):
        q = lvm_quit(self.handle)
        if q != 0:
            raise HandleError("Failed to release LVM handle.")