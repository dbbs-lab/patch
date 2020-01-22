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
