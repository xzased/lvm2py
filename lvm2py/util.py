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

from ctypes import cast
from conversion import *
from exception import *
from . import handle


def vgscan():
    lvm_scan(handle)
    vg_list = []
    vgnames = lvm_list_vg_names(handle)
    if dm_list_empty(vgnames):
        return vg_list
    vg = vgnames.contents.n
    while vg:
        c = cast(vg, POINTER(lvm_str_list))
        vg_list.append(c.contents.str)
        if dm_list_end(vgnames, vg):
            # end of linked list
            break
        vg = vg.contents.n
    return vg_list


def reset_handle(handle):
    q = lvm_quit(handle)
    if q != 0:
        raise HandleError("Failed to delegate LVM handle.")
    new = lvm_init()
    return new