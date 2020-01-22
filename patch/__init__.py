from .interpreter import PythonHocInterpreter

__version__ = "1.0.2"

p = PythonHocInterpreter()
p.load_file("stdrun.hoc")
