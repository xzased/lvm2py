Introduction
============

lvm2py is a ctypes based binding for lvm's liblvm2app api. There are some limitations
to what it can do compared to the command line options available. For example, the 
resize of Physical and Logical volumes is not implemented in the api yet.

As of February 2019, there were two people who had forked and patched
the upstream repo at https://github.com/xzased/lvm2py and this branch
just combines their minimal changes.

Downloads
=========

You can download the package from PyPi:

    http://pypi.python.org/pypi/lvm2py/

or checkout lvm2py on github:

    http://github.com/xzased/lvm2py


Installation
============

You can get reparted using pip to install it from PyPI::

    pip install -U lvm2py

.. note::
    You must have liblvm2app installed and available from your LD_LIBRARY_PATH


Documentation
=============

You can view the documentation and quickstart guide here:

    http://xzased.github.com/lvm2py
