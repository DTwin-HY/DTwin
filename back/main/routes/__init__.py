import pkgutil
import importlib
"""
This package imports all route modules in the current directory.
"""
__all__ = []

for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f"{__name__}.{module_name}")
    globals()[module_name] = module
    __all__.append(module_name)