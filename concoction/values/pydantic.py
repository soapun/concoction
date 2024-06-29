from pydantic import Field


def Value(prefix: str):
    def default_factory():
        from concoction.core import global_config

        value = global_config.get(prefix)
        if value is None:
            raise KeyError("{0} not found in global_config".format(prefix))
        return value

    return Field(default_factory=default_factory, validate_default=True)
