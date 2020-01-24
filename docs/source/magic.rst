Magic methods
=============

\_\_neuron\_\_
--------------

*Get the object's NEURON pointer*

Whenever an object with this method present is sent to the NEURON HOC interpreter, the
result of this method is passed instead. This allows Python methods to encapsulate NEURON
pointers transparently

\_\_netcon\_\_
--------------

*Get the object's NetCon pointer*

Whenever an object with this method present is used in a NetCon call, the result of this
method is passed instead. The connection is stored on the original object. This allows to
simplify the calls to NetCon, or to add more elegant default behavior, like inserting the
connection on a random segment of a section and being able to use just ``p.NetCon(section,
synapse)``.
