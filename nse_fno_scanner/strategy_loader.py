import importlib
from typing import Callable, Iterable, List

Strategy = Callable[[Iterable[str]], List[str]]


def load_strategy(path: str) -> Strategy:
    """Load a strategy callable from ``module:function`` string."""
    if ":" not in path:
        raise ValueError("Strategy path must be in module:function format")
    module_name, func_name = path.split(":", 1)
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)
    if not callable(func):
        raise TypeError(f"{path} is not callable")
    return func
