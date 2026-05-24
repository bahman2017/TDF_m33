"""Verify package and subpackage imports."""

import importlib

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "tdf_m33",
        "tdf_m33.constants",
        "tdf_m33.data",
        "tdf_m33.models",
        "tdf_m33.fitting",
        "tdf_m33.plotting",
        "tdf_m33.lensing",
        "tdf_m33.utils",
    ],
)
def test_import_module(module_name: str) -> None:
    mod = importlib.import_module(module_name)
    assert mod is not None


def test_package_version() -> None:
    import tdf_m33

    assert isinstance(tdf_m33.__version__, str)
    assert tdf_m33.__version__
