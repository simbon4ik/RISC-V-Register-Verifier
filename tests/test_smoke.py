import pytest
from src import sequencer


def test_imports_work():
    # smoke-test: модуль импортируется и функция существует
    assert hasattr(sequencer, "sweep_read_all")
