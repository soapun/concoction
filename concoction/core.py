import warnings
from functools import wraps
from typing import Any, Dict

from benedict import benedict

global_config: benedict = benedict()


def set_global_config(config: Dict[str, Any]):
    if not isinstance(config, Dict):
        raise TypeError(
            "Config must be of type Dict[str, Any], got {0}".format(
                type(config)
            )
        )
    for key in config.keys():
        if not isinstance(key, str):
            raise TypeError(
                "All keys in config must be of type str, found {0} of type {1}".format(
                    key, type(key)
                )
            )
    global global_config
    global_config = benedict(config)


class Configuration:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def __call__(self, cls):
        original_init = cls.__init__

        @wraps(cls.__init__)
        def wrapper(_self, *args, **kwargs):
            if not args and not kwargs:
                config_section = global_config.get(self.prefix, {})
                if not config_section:
                    warnings.warn(
                        UserWarning(
                            "Configuration section {0} for {1} not found".format(
                                self.prefix, cls.__name__
                            )
                        ),
                        stacklevel=2,
                    )
                kwargs.update(config_section)
            return original_init(_self, *args, **kwargs)

        cls.__init__ = wrapper
        return cls
