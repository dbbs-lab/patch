[![Build Status](https://travis-ci.org/Helveg/patch.svg?branch=master)](https://travis-ci.org/Helveg/patch)
[![codecov](https://codecov.io/gh/Helveg/patch/branch/master/graph/badge.svg)](https://codecov.io/gh/Helveg/patch)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/patch/badge/?version=latest)](https://patch.readthedocs.io/en/latest/?badge=latest)

_*No ducks were punched during the construction of this monkey patch._

# Installation

```
pip install nrn-patch
```

![Inline replacement of NEURON by
Patch](https://s5.gifyu.com/images/ezgif.com-video-to-gif-13b2788fb8bc11ca7.gif)

Be aware that the interface is currently incomplete, this means that most parts are still
"just" NEURON. I've only patched holes I frequently encounter myself when using the
`h.Section`, `h.NetStim` and `h.NetCon` functions. Feel free to open an issue or fork this
project and open a pull request for missing or broken parts of the interface.

# Philosophy

Python interfaces should be Pythonic, this wrapper offers just that:

  - Full Python objects: each wonky C-like NEURON object is wrapped in a
    full fledged Python object, easily handled and extended through
    inheritance.
  - Duck typed interface: take a look at the magic methods I use and any
    object you create with those methods present will work just fine
    with Patch.
  - Correct garbage collection, objects connected to eachother don't
    dissapear: Objects that rely on eachother store a reference to
    eachother. As is the basis for any sane object oriented interface.
  - Explicit exceptions: I catch silent failures and gotchas and raise
    semantic errors with a class hierarchy instead for granular
    exception handling.

**Warning:** When running MPI simulations errors cannot be caught due to a
[bug](https://github.com/neuronsimulator/nrn/issues/1112) in NEURON where every
exception results in NEURON calling `MPI_Abort` and shutting down the
simulation. If this leads to confusing failure modes please post an issue with
your Patch code to the GitHub repo!

# Basic usage

Use it like you would use NEURON. The wrapper doesn't make any changes to the interface,
it just patches up some of the more frequent and ridiculous gotchas.

Patch supplies a new HOC interpreter `p`, the `PythonHocInterpreter` which wraps the
standard HOC interpreter `h` provided by NEURON. Any objects returned will either be
`PythonHocObject`'s wrapping their corresponding NEURON object, or whatever NEURON
returns.

When using just Patch the difference between NEURON and Patch objects is handled
transparently, but if you wish to mix interpreters you can transform all Patch objects
back to NEURON objects with `obj.__neuron__()`.

``` python
from patch import p
import glia as g

section = p.Section()
point_process = g.insert(section, "AMPA")
stim = p.NetStim()
stim.start = 10
stim.number = 5
stim.interval = 10

# And here comes the magic! This explicitly defined connection
# isn't immediatly garbage collected! What a crazy world we live in.
# Has science gone too far?
p.NetCon(stim, point_process)

# It's fully compatible using __neuron__
from neuron import h
nrn_section = h.Section()
nrn_section.connect(section.__neuron__())
```

# Magic methods

## \_\_neuron\_\_

_Get the object's NEURON pointer_

Whenever an object with this method present is sent to the NEURON HOC interpreter, the
result of this method is passed instead. This allows Python methods to encapsulate NEURON
pointers transparently

## \_\_netcon\_\_

_Get the object's NetCon pointer_

Whenever an object with this method present is used in a NetCon call, the result of this
method is passed instead. The connection is stored on the original object. This allows to
simplify the calls to NetCon, or to add more elegant default behavior, like inserting the
connection on a random segment of a section and being able to use just ``p.NetCon(section,
synapse)``
