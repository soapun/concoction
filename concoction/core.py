import warnings
from functools import wraps
from typing import Any, Dict

from benedict import benedict

global_config: benedict = benedict()


def set_global_config(config: Dict[str, Any]):
    if not isinstance(config, Dict):
        raise TypeError("Config must be of type Dict[str, Any]")
    for key in config.keys():
        if not isinstance(key, str):
            raise TypeError("All keys in config must be of type str")
    global global_config
    global_config = benedict(config)


class Configuration:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def __call__(self, cls):
        @wraps(cls)
        def wrapper(*args, **kwargs):
            if not args and not kwargs:
                config_section = global_config.get(self.prefix, {})
                if not config_section:
                    warnings.warn(UserWarning("Configuration section for {cls.__name__} not found"), stacklevel=2)
                kwargs.update(config_section)
            return cls(*args, **kwargs)

        return wrapper
