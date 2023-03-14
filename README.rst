.. _pyDALAnvilWorksDev : https://github.com/benlawraus/pyDALAnvilWorksDev
.. _pyDALAnvilWorks : https://github.com/benlawraus/pyDALAnvilWorks
.. _yaml2schema : https://github.com/benlawraus/yaml2schema
.. _anvil_extras : https://github.com/benlawraus/anvil_extras
.. _anvil-extras : https://github.com/anvilistas/anvil-extras

anvil_extras on a Laptop
================================
This is part of a set of repositories for the Test Driven Development of anvil.works apps.

It belongs with the following repositories:

`pyDALAnvilWorksDev <https://github.com/benlawraus/pyDALAnvilWorksDev>`_
  The top level repository used as scaffold
    `pyDALAnvilWorks <https://github.com/benlawraus/pyDALAnvilWorks>`_
      used to set up anvil.works functionality
    `yaml2schema <https://github.com/benlawraus/yaml2schema>`_
      used to convert anvil.yaml to a database schema
    `anvil_extras <https://github.com/benlawraus/anvil_extras>`_
      used to add functionality to anvil.works

This repository is a copy of `anvil-extras <https://github.com/anvilistas/anvil-extras>`_ with the changes that will
allow it to be used within the `pyDALAnvilWorksDev <https://github.com/benlawraus/pyDALAnvilWorks>`_ scaffold, running on a local computer.

It is not intended to be used as a stand alone repository or a substitute for `anvil-extras <anvil-extras>`_ within
an anvil.works app.

It is a work in progress. So far the only changes have been to:
  * client_code/storage.py
