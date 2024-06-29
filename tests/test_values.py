from dataclasses import dataclass

import pytest
from pydantic import BaseModel

from concoction.core import set_global_config
from concoction.values.dataclass import Value as ValueDataclass
from concoction.values.pydantic import Value as ValuePydantic


@pytest.fixture(scope="module", autouse=True)
def global_config():
    config = {
        "app": {
            "service": {
                "name": "test",
                "workers": "4"
            }
        }
    }
    set_global_config(config)
    yield
    set_global_config({})


class ServiceConfigPydantic(BaseModel):
    name: str = "default"
    workers: int = ValuePydantic("app.service.workers")


@dataclass
class ServiceConfigDataclass:
    name: str = "default"
    workers: int = ValueDataclass("app.service.workers")


class ConfigMissingPydantic(BaseModel):
    workers: int = ValuePydantic("app.db.workers")


class ConfigMissingDataclass(BaseModel):
    workers: int = ValueDataclass("app.db.workers")


def test_pydantic_no_args():
    config = ServiceConfigPydantic()
    assert config.name == "default"
    assert config.workers == 4


def test_pydantic_args():
    config = ServiceConfigPydantic(name="test")
    assert config.name == "test"
    assert config.workers == 4


def test_dataclass_no_args():
    config = ServiceConfigDataclass()
    assert config.name == "default"
    assert config.workers == "4"  # since dataclass doesn't cast


def test_dataclass_args():
    config = ServiceConfigDataclass(name="test")
    assert config.name == "test"
    assert config.workers == "4"


def test_missing_field_pydantic():
    with pytest.raises(KeyError):
        _ = ConfigMissingPydantic()


def test_missing_field_dataclass():
    with pytest.raises(KeyError):
        _ = ConfigMissingDataclass()
