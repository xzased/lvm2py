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

from ctypes.util import find_library
from ctypes import *
from .exception import HandleError


lib = find_library("lvm2app")

if not lib:
    raise Exception("LVM library not found.")

lvmlib = CDLL(lib)

class lvm(Structure):
    pass

lvm_t = POINTER(lvm)

# Initialize library
lvm_init = lvmlib.lvm_init
lvm_init.argtypes = [c_char_p]
lvm_init.restype = lvm_t

# Set lvm handle
handle = lvm_init("/etc/lvm")
if not type(handle) == lvm_t:
    raise HandleError("Failed to initialize LVM handle.")


from .vg import VolumeGroup
from .pv import PhysicalVolume