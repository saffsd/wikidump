wikidump
==========================

Introduction
------------

This module contains code for manipulating wikipedia dumps available from
http://download.wikimedia.org/backup-index.html

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
