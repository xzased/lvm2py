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

class HandleError(Exception):
    """
    Raised when the lvm handle for LVM, VolumeGroup, PhysicalVolume or
    LogicalVolume is null or for some reason it can't be obtained (bad parameters,
    duplicate namespaces, etc...)
    """
    pass

class CommitError(Exception):
    """
    Raised when there is an error in committing changes to lvm due to invalid
    actions such as initiating devices as physical volumes that are already
    associated to another volume group or trying to perform operations on a
    read-only volume group.
    """
    pass