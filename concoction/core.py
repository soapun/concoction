import warnings
from functools import wraps
from typing import Any, Dict, Type, Callable, List

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
    prefix_to_class: Dict[str, Type] = dict()
    require_unique_prefixes: bool = True

    post_init_hooks: List[Callable[[object], None]] = []

    def __init__(self, prefix: str):
        self.prefix = prefix

    def __call__(self, cls):
        original_init = cls.__init__

        @wraps(cls.__init__)
        def wrapper(_self, *args, **kwargs):
            if args or kwargs:
                return original_init(_self, *args, **kwargs)

            config_section = global_config.get(self.prefix, {})
            if not config_section:
                warnings.warn(
                    UserWarning(
                        "Configuration section {0} for {1} not found".format(
                            self.prefix, cls
                        )
                    ),
                    stacklevel=2,
                )
            kwargs.update(config_section)

            obj = original_init(_self, *args, **kwargs)
            for post_init_hook in self.post_init_hooks:
                post_init_hook(obj)
            return obj

        if self.prefix in self.prefix_to_class:
            message = (
                "Configuration section {0} is already binded to {1}".format(
                    self.prefix, self.prefix_to_class[self.prefix]
                )
            )
            if self.require_unique_prefixes:
                raise KeyError(message)
            warnings.warn(UserWarning(message), stacklevel=2)

        self.prefix_to_class[self.prefix] = cls
        cls.__init__ = wrapper
        return cls
