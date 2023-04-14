anvil_extras on a Laptop
================================
This is part of a set of repositories for the Test Driven Development of anvil.works apps.

It belongs with the following repositories:

- [anvil_works_design_test](https://github.com/benlawraus/anvil_works_design_test)
The top level repository used as scaffold
- [anvil](https://github.com/benlawraus/anvil) Mock classes for anvil.works
- [_anvil_designer](https://github.com/benlawraus/_anvil_designer)
used to generate client_code mock classes
- [yaml2schema](https://github.com/benlawraus/yaml2schema)
used to convert `anvil.yaml` to a database schema
- [anvil_extras](https://github.com/benlawraus/anvil_extras)
used to add test functionality to anvil.works



This repository is a copy of [anvil-extras](https://github.com/anvilistas/anvil-extras) with the changes that will
allow it to be used within the  [anvil_works_design_test](https://github.com/benlawraus/anvil_works_design_test)
scaffold, running on a local computer.

It is not intended to be used as a stand alone repository or a substitute for [anvil-extras](https://github.com/anvilistas/anvil-extras) within
an anvil.works app.

It is a work in progress. So far the only changes have been to:
  * client_code/storage.py
  * client_code/augment.py
