import inspect

import pytest
from pydantic import BaseModel

from concoction.core import set_global_config, Configuration


@pytest.fixture(scope="module", autouse=True)
def global_config():
    config = {
        "app": {
            "service": {"name": "test", "version": "0.0.0", "workers": "4"},
            "db": {
                "connection": "test",
                "user": "admin",
            },
        }
    }
    set_global_config(config)
    yield
    set_global_config({})


@Configuration("app.service")
class ServiceConfig(BaseModel):
    name: str = "default"
    version: str = "default"
    workers: int = 1


@Configuration("app.db")
class DbConfig(BaseModel):
    connection: str = "default"
    user: str = "default"


@Configuration("app.missing")
class MissingConfig(BaseModel):
    name: str = "default"


def test_registered_classes():
    assert Configuration.prefix_to_class == {
        "app.service": ServiceConfig,
        "app.db": DbConfig,
        "app.missing": MissingConfig,
    }


def test_post_init_hooks():
    x = 0

    def hook(*args, **kwargs):
        nonlocal x
        x = 1

    Configuration.post_init_hooks.append(hook)
    ServiceConfig()
    assert x == 1
    Configuration.post_init_hooks = []


def test_require_unique_prefixes():
    with pytest.raises(KeyError):

        @Configuration("app.service")
        class SecondServiceConfig:  # noqa
            name: str = "default"
            version: str = "default"
            workers: int = 1

    Configuration.require_unique_prefixes = False

    with pytest.warns(UserWarning):

        @Configuration("app.service")
        class ThirdServiceConfig:  # noqa
            name: str = "default"
            version: str = "default"
            workers: int = 1

    Configuration.require_unique_prefixes = True


def test_no_args():
    service_config = ServiceConfig()

    assert service_config.name == "test"
    assert service_config.version == "0.0.0"
    assert service_config.workers == 4


def test_correct_decorating():
    assert inspect.isclass(ServiceConfig)


def test_args():
    service_config = ServiceConfig(name="args")

    assert service_config.name == "args"
    assert service_config.version == "default"
    assert service_config.workers == 1


def test_multiple_configs():
    service_config = ServiceConfig()
    db_config = DbConfig()

    assert service_config.name == "test"
    assert service_config.version == "0.0.0"
    assert service_config.workers == 4

    assert db_config.connection == "test"
    assert db_config.user == "admin"


def test_missing_prefix():
    with pytest.warns(UserWarning):
        missing_config = MissingConfig()
        assert missing_config.name == "default"


def test_parent_merging():
    parent_prefix = "app.parent"
    child_prefix = "app.child"

    set_global_config(
        {
            "app": {
                "parent": {
                    "base_only": "base",
                    "both": "base",
                },
                "child": {
                    "child_only": "derived",
                    "both": "derived",
                },
            }
        }
    )

    @Configuration(parent_prefix)
    class ParentConfig(BaseModel):
        base_only: str
        both: str

    @Configuration(child_prefix, merge_parents=True)
    class ChildConfig(ParentConfig):
        child_only: str

    child = ChildConfig()
    assert child.base_only == "base"
    assert child.child_only == "derived"
    assert child.both == "derived"
