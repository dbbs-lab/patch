.. Patch documentation master file, created by
   sphinx-quickstart on Fri Jan 24 15:06:28 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Patch's documentation!
=================================

.. image:: https://badge.fury.io/gh/Helveg%2Fpatch.svg
    :target: https://badge.fury.io/gh/Helveg%2Fpatch

.. image:: https://travis-ci.com/Helveg/patch.svg?branch=master
    :target: https://travis-ci.com/Helveg/patch

.. image:: https://codecov.io/gh/Helveg/patch/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/Helveg/patch

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   sections
   magic
   patch

Installation
------------

Patch can be installed using::

   pip install nrn-patch

Known unpatched holes
---------------------

* When creating point processes the returned object is unwrapped.
  This can be resolved using `Glia <https://github.com/dbbs-lab/glia>`_, or by
  using this syntax:

.. code-block:: python

    # In neuron
    process = h.MyMechanismName(my_section(0.5), *args, **kwargs)
    # In patch
    point_process = p.PointProcess(p.MyMechanismName, my_section(0.5), *args, **kwargs)


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
