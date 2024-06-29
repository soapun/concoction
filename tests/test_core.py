import pytest
from pydantic import BaseModel

from concoction.core import set_global_config, Configuration


@pytest.fixture(scope="module", autouse=True)
def global_config():
    config = {
        "app": {
            "service": {
                "name": "test",
                "version": "0.0.0",
                "workers": "4"
            },
            "db": {
                "connection": "test",
                "user": "admin",
            }
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


def test_no_args():
    service_config = ServiceConfig()

    assert service_config.name == "test"
    assert service_config.version == "0.0.0"
    assert service_config.workers == 4


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
