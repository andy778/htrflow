"""Fast, download-free checks that the installed dependencies match what
htrflow declares in `pyproject.toml`. Meant to catch broken or incompatible
versions immediately on a dependency-update PR, before the slower model-based
tests run.
"""

import importlib
import importlib.metadata as metadata

import pytest
from packaging.requirements import Requirement


def _core_requirements() -> list[Requirement]:
    reqs = metadata.requires("htrflow") or []
    return [Requirement(r) for r in reqs if not Requirement(r).marker]


@pytest.mark.parametrize("requirement", _core_requirements(), ids=lambda r: r.name)
def test_installed_version_satisfies_pyproject(requirement: Requirement):
    installed_version = metadata.version(requirement.name)
    assert requirement.specifier.contains(installed_version, prereleases=True), (
        f"installed {requirement.name}=={installed_version} does not satisfy "
        f"the constraint '{requirement}' declared in pyproject.toml"
    )


@pytest.mark.parametrize(
    "module_name",
    ["torch", "transformers", "ultralytics", "cv2", "xmlschema", "pydantic", "jinja2"],
)
def test_core_dependency_imports(module_name: str):
    importlib.import_module(module_name)
