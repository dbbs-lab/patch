# 2.0.2

* Created a module class for the root module with p as a property so that neuron isn't
  imported on patch import, until patch.p is accessed.

# 2.0.1

* Improved missing `nrnmpi_init` handling.

# 2.0

* Renamed `p.pc` to `p.parallel`
* Throw a warning when `h.nrnmpi_init` is missing and `p.parallel` is used.

# 1.4

* Added `ParallelCon` for parallel simulations.

# 1.3.2

* Fixed a bug with the previous distribution where the VecStim mod file was missing.

# 1.3.1

* Added better error handling for NEURON errors.
* Added checks so that `continuerun` and `run` can only be used after `finitialize`

# 1.3.0

* Added extensions:
  * HOC extensions: hoc files that can be packaged along and loaded.
  * MOD extensions: A Glia package `patch_extensions` is installed along with patch so
    that any mod files required to run patch are automatically compiled and loaded.
* Added `VecStim`, which can stimulate according to arbitrary patterns.
* Added `pattern` keyword argument to `PointProcess.stimulate` so that a VecStim is
  created.

# 1.2.1

* Added ReadTheDocs documentation
* Added `time` property to the interpreter which returns a singleton recording device of
  the timesteps in the simulation.

# 1.2

* Added `stimulate` method to point processes. This creates a NetStim connected to it.
* Added `connection` function in the root module that retrieves a NetCon between 2 objects
  if they are connected.
* Added default `__netcon__` and `__record__` behavior to Sections, they will now refer to
  the Segment at x=0.5.

# 1.1

* Added `__netcon__` and `__record__` magic methods for better default behavior in
  `p.NetCon` and `Vector.record` respectively.
* The _RunTimeError: hoc error_ for NetCon gets caught and a proper `HocConnectError` is
  raised.
* `PythonHocObject`s now store a reference to the Patch interpreter instead of NEURON's.
* Added `Section.connect_points`, a shorthand function to NetCon a point on a section to
  a point process.
* Added the `Section.record` function to record a point on the section.
* Added a wrapper for `Vector` with an improved `record` function.
* The PythonHocInterpreter always loads `stdrun.hoc`.


# 1.0.2

* `Section.insert` now returns itself as a patched Section.
