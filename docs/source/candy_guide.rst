###########
Candy Guide
###########

===========
Referencing
===========

All objects in Patch that depend on each other reference each other, meaning that Python
won't garbage collect parts of your simulation that you explicitly defined. An example of
this is that when you create a synapse and a NetStim and connect them together with a
NetCon, you only have to hold on to 1 of the variables for Patch to know that if you're
holding on to a NetCon you are *most likely* interested in the parts it is connected to.
There is no longer a need to store every single NEURON variable in a list or on an object
somewhere. This drastically cleans up your code.

===================
Sections & Segments
===================

* When connecting Sections together they all reference each other.
* Whenever you're using a Section where a Segment is expected, a default Segment will be
  used (Segment 0.5):

.. code-block:: python

  s = p.Section()
  p.ExpSyn(s) # syn = h.ExpSyn(s(0.5))

* Whenever a Section/Segment is recorded or connected and a NEURON scalar is expected
  ``_ref_v`` is used:

.. code-block:: python

  s = p.Section()
  v = p.Vector()
  v.record(s) # v.record(s(0.7)._ref_v)

* Sections can record themselves at multiple points:

.. code-block:: python

  s = p.Section()
  s.record() # Creates a vector, makes it record s(0.5)._ref_v and stores it as a recorder
  s.record(0.7) # Records s(0.5)._ref_v

  plt.plot(list(s.recordings[0.5]), list(p.time))

* Sections can connect themselves to a PointProcess target with ``.connect_points``, which
  handles NetCon stack access transparently:

.. code-block:: python

  s = p.Section()
  target_syn = p.Section().synapse(p.ExpSyn)
  s.connect_points(target_syn) # No more s.push() and h.pop_section() required for NetCon.
