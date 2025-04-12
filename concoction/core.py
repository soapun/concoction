import warnings
from functools import wraps
from typing import Any, Dict, Type, Callable, List

from bidict import bidict
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
    prefix_to_class: bidict[str, Type] = bidict()
    require_unique_prefixes: bool = True

    post_init_hooks: List[Callable[[object], None]] = []

    def __init__(self, prefix: str, merge_parents: bool = False):
        self.prefix = prefix
        self.merge_parents = merge_parents

    def get_parent_prefixes(self, cls) -> List[str]:
        parent_prefixes = []
        for base in cls.__mro__:
            if base is cls:
                continue
            if (
                base in self.prefix_to_class.inverse
                and self.prefix_to_class.inverse[base] not in parent_prefixes
            ):
                parent_prefixes.append(self.prefix_to_class.inverse[base])
        return parent_prefixes

    def __call__(self, cls):
        original_init = cls.__init__

        @wraps(cls.__init__)
        def wrapper(_self, *args, **kwargs):
            if args or kwargs:
                return original_init(_self, *args, **kwargs)

            parent_prefixes = (
                self.get_parent_prefixes(cls) if self.merge_parents else []
            )
            # reverse order for merging, parent to child
            for parent_prefix in reversed(parent_prefixes):
                parent_config = global_config.get(parent_prefix, {})
                kwargs.update(parent_config)

            config_block = global_config.get(self.prefix, {})
            if not config_block:
                warnings.warn(
                    UserWarning(
                        "Configuration block {0} for {1} not found".format(
                            self.prefix, cls
                        )
                    ),
                    stacklevel=2,
                )
            kwargs.update(config_block)

            obj = original_init(_self, *args, **kwargs)
            for post_init_hook in self.post_init_hooks:
                post_init_hook(obj)
            return obj

        if self.prefix in self.prefix_to_class:
            message = (
                "Configuration block {0} is already binded to {1}".format(
                    self.prefix, self.prefix_to_class[self.prefix]
                )
            )
            if self.require_unique_prefixes:
                raise KeyError(message)
            warnings.warn(UserWarning(message), stacklevel=2)

        self.prefix_to_class[self.prefix] = cls
        cls.__init__ = wrapper
        return cls
