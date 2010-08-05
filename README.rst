wikidump
==========================

Introduction
------------

This module contains code for manipulating wikipedia dumps available from
http://download.wikimedia.org/backup-index.html


Installation
------------

This module is published on `PyPI`_ and can be installed with easy_install

For example:

  easy_install wikidump

Alternatively, you can use pip:

  pip install wikidump

I highly recommend using `virtualenv`_ to isolate the install environment.

For those on ubuntu systems, a built package is available in a `PPA`_. 
Please go to the PPA for details on how to install from it.


.. _PyPI: http://pypi.python.org/pypi/wikidump
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _PPA: https://launchpad.net/~saffsd/+archive/wikidump

Configuration
-------------

Upon first importing the module, a file 'wikidump.cfg' will be created.
Modify the paths in this file to point to your data. 

- scratch : where indices are stores (must be writeable)
- xml_dumps : where the xml dumps are located (can be read-only)

Usage
-----

In addition to python modules, wikidump also comes with a command-line
tool to quickly access wikidump functionality. Run `wikidump help` 
for a list of options.

Credits
-------

- `Distribute`_
- `Buildout`_
- `modern-package-template`_

.. _Buildout: http://www.buildout.org/
.. _Distribute: http://pypi.python.org/pypi/distribute
.. _`modern-package-template`: http://pypi.python.org/pypi/modern-package-template
