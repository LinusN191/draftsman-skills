"""Bootstrap importer for the hyphenated ``zone-derivation`` package.

Python disallows hyphens in regular module names, so the test suite uses
``importlib.util.spec_from_file_location`` to load the package under the
alias ``zone_derivation``. All test modules import the alias rather than
fighting the directory name.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys


def load_zone_derivation():  # type: ignore[no-untyped-def]
    """Load the zone-derivation package and return the module object."""
    if "zone_derivation" in sys.modules:
        return sys.modules["zone_derivation"]

    pkg_path = pathlib.Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location(
        "zone_derivation",
        pkg_path / "__init__.py",
        submodule_search_locations=[str(pkg_path)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to build spec for {pkg_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["zone_derivation"] = module
    spec.loader.exec_module(module)
    return module


zone_derivation = load_zone_derivation()
common = zone_derivation.common
bath = zone_derivation.bath
pool = zone_derivation.pool
sauna = zone_derivation.sauna
medical = zone_derivation.medical
elv = zone_derivation.elv
