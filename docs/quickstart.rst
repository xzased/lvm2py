Quickstart
================
Here is the guide for the impatient::

    from lvm2py import *

    # Initialize LVM
    lvm = LVM()

    # if you want to set the system directory use the following class method
    lvm.set_system_dir("/path/to/dir")

You can create volume groups like this::

    # returns an instance of VolumeGroup
    vg = lvm.create_vg("myvg", ["/dev/sdb1", "/dev/sdb2"])

.. note::

    You must define the devices to be initialized as physical volumes as a list.

To retrieve existing volume groups you can call vgscan or get them by name::

    # returns a list of VolumeGroup instances
    vgs = lvm.vgscan()

    # get by name
    vg1 = lvm.get_vg("myvg")

    # get by name and activate write mode
    vg2 = lvm.get_vg("myvg", "w")

You can add physical volumes (volume group must be in write mode)::

    # set volume group in write mode
    if vg.mode == "r":
        vg.set_mode("w")

    # add physical volume (the devices are initialized by this method, no previous
    # modification is needed.
    pvx = vg.add_pv("/dev/sdbX")


Now that you have your physical volumes, you can create logical volumes::

    lv1 = vg.create_lv("mylv", 40, "MiB")

We can scan the volume group::

    # return a list of PhysicalVolume and LogicalVolume instances
    pvs = vg.pvscan()
    lvs = vg.lvscan()

Now let's destroy everything::

    # one logical volume at a time
    vg.remove_lv(lv1)

    # or burn
    vg.remove_all_lvs()

    # You can remove a volume group once all logical volumes are removed
    lvm.remove_vg(vg)

    # but if you want to remove physical volumes, use the following method
    vg.remove_pv(pvx)

    # If you remove all physical volumes, the volume group will be destroyed once
    # the last physical volume is removed.


That's it for now, have fun. Checkout the module reference for more available options.

.. note::
    On some distributions, the liblvm2app library is still on it's 2010 release, this will make lvm2py
    raise an AttributeError on import. Also, it is not possible to operate on orphaned physical volumes,
    quoting documentation in the liblvm2app library:

        *Physical volume handling should not be needed anymore. Only physical volumes*
        *bound to a vg contain useful information. Therefore the creation,*
        *modification and the removal of orphan physical volumes is not suported.*