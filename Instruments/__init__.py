from os.path import dirname, basename, isfile
import glob
from importlib import import_module
import Instruments.devGlobalFunctions

# __all__ = ["devGlobalFunctions"]

def load_instruments():
    # Step 1. Find all python files in this directory
    names = glob.glob(dirname(__file__)+"/*.py")

    # Step 2. Import all the python files
    modules = [import_module("{}.{}".format(__name__, basename(f)[:-3])) for f in names if isfile(f) and
               (not f.endswith('__init__.py') and not f.endswith('devGlobalFunctions.py'))]

    # Step 3. Extract the instrument from each module and return it
    return {m.instrument.name:m.instrument for m in modules}

def instrument_names():
    instruments = load_instruments()

    return list(instruments.keys())
