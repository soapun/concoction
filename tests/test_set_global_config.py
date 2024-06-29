import pytest

from concoction.core import set_global_config


def test_not_dict():
    with pytest.raises(TypeError):
        set_global_config([1, 2, 3])


def test_bad_keys():
    with pytest.raises(TypeError):
        set_global_config({"1": 2, 1: 2})
