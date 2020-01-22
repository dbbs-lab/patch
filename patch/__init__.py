from .interpreter import PythonHocInterpreter

__version__ = "1.1.0"

p = PythonHocInterpreter()
p.load_file("stdrun.hoc")
