#####################
Connecting components
#####################

===================
Connecting sections
===================

To other sections
=================

.. container:: left-col

    Connecting sections together is the basic way of constructing cells in NEURON. You can
    do so using the ``Section.connect`` method.

.. container:: content-tabs right-col

    .. tab-container:: tab1
        :title: Patch

        .. code-block:: python

            from patch import p
            s = p.Section()
            s2 = p.Section()
            s.connect(s2)

    .. tab-container:: tab2
        :title: NEURON

        .. code-block:: python

            from neuron import h
            s = h.Section()
            s2 = h.Section()
            s.connect(s2)


===================
Network connections
===================

TO DO



In parallel simulations
=======================


.. container:: left-col

    In Patch most of the parallel context is managed for you, and you can use the
    :func:`.interpreter.PythonHocInterpreter.ParallelCon` method to either connect an
    output (cell soma, axons, ...) to a GID or a GID to an input (synapse on postsynaptic
    cell, ...)

.. container:: content-tabs right-col

    .. tab-container:: tab1
        :title: Patch

        Detecting the spikes of a Section and connecting them to GID 1:

        .. code-block:: python

            from patch import p
            gid = 1
            s = p.Section()
            nc = p.ParallelCon(s, gid)

        Connecting the spikes of GID 1 to a synapse:

        .. code-block:: python

            from patch import p
            gid = 1
            syn = p.Section().synapse(p.SynExp)
            nc = p.ParallelCon(gid, syn)

    .. tab-container:: tab2
        :title: NEURON

        Detecting the spikes of a Section and connecting them to GID 1:

        .. code-block:: python

            from neuron import h
            gid = 1
            h.nrnmpi_init()
            pc = h.ParallelContext()
            s = h.Section()
            nc = h.NetCon(s(0.5)._ref_v, None)
            pc.set_gid2node(gid, pc.id())
            pc.cell(gid, nc)

        Connecting the spikes of GID 1 to a synapse:

        .. code-block:: python

            from neuron import h
            gid = 1
            h.nrnmpi_init()
            pc = h.ParallelContext()
            s = h.Section()
            syn = h.SynExp(s)
            pc.gid_connect(gid, syn)
