import importlib.machinery
import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def qe_module():
    qe_path = Path(__file__).resolve().parents[1] / "qe"
    loader = importlib.machinery.SourceFileLoader("qe_under_test", str(qe_path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module
