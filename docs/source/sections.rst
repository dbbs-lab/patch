Sections
========

.. container:: left-col

    Sections are cilindrical representations of pieces of a cell. They have a length and a
    diameter. Sections are the main building block of a simulation in NEURON.

    You can use the ``.connect`` method to connect :class:`Sections <.objects.Section>`
    together.

    Sections can be subdivided into :class:`Segments <.objects.Segment>` by specifying
    ``nseg``, the simulator calculates the voltage for each segment, thereby affecting the
    spatial resolution of the simulation. The position of a segment is represented by its
    normalized position along the axis of the Segment. This means that a Segment at x=0.5
    is in the middle of the Section. By default every section consists of 1 segment and
    the potential will be calculated for 3 points: At the start (0) and end (1) of the
    section, and in the middle of every segment (0.5). For 2 segments the simulator would
    calculate at 0, 0.333..., 0.666... and 1.

.. container:: content-tabs right-col

    .. tab-container:: tab1
        :title: Patch

        .. code-block:: python

            from patch import p
            s = p.Section()
            s.L = 40
            s.diam = 0.4
            s.nseg = 11

            s2 = p.Section()
            s.connect(s2)

    .. tab-container:: tab2
        :title: NEURON

        .. code-block:: python

            from neuron import h
            s = h.Section()
            s.L = 40
            s.diam = 0.4
            s.nseg = 11

            s2 = h.Section()
            s.connect(s2)

Retrieving segments
-------------------

.. container:: left-col


    Sections can be called with an x to retrieve the segment at that x. The segments of a
    Section can also be iterated over.

.. container:: content-tabs right-col

    .. tab-container:: tab1
        :title: Patch

        .. code-block:: python

            s.nseg = 5
            seg05 = s(0.5)
            print(seg05)
            for seg in s:
                print(seg)

    .. tab-container:: tab2
        :title: NEURON

        .. code-block:: python

            s.nseg = 5
            seg05 = s(0.5)
            print(seg05)
            for seg in s:
                print(seg)

Recording
---------

.. container:: left-col

    You can tell Patch to record the membrane potential of your Section at one or
    multiple locations by calling the ``.record`` function and giving it an ``x``. If
    ``x`` is omitted ``0.5`` is used.

    In NEURON you'd have to create a :class:`Vector <.objects.Vector>` and keep track of
    it somewhere and find a way to link it back to the Section it recorded, in Patch a
    section automatically stores its recording vectors in ``section.recordings``.

.. container:: content-tabs right-col

    .. tab-container:: tab1
        :title: Patch

        .. code-block:: python

            s.record(x=1.0)

    .. tab-container:: tab2
        :title: NEURON

        .. code-block:: python

            v = h.Vector()
            v.record(s(1.0))
            all_recorders.append(v)

Position in space
-----------------


.. container:: left-col

    With Patch it's very straightforward to define the 3D path of your Section through
    space. Call the ``.add_3d`` function with a 2D array of containing the xyz data of
    your points. Optionally, you can pass another array of diameters.

.. container:: content-tabs right-col

    .. tab-container:: tab1
        :title: Patch

        .. code-block:: python

            s.add_3d([[0, 0, 0], [2, 2, 2]], diameters)

    .. tab-container:: tab2
        :title: NEURON

        .. code-block:: python

            s.push()
            points = [[0, 0, 0], [2, 2, 2]]
            for point, diameter in zip(points, diameters):
                h.pt3dadd(*point, diameter)
            h.pop_section()
