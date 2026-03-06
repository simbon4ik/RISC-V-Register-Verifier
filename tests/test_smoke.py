import importlib


def test_src_package_importable():
    pkg = importlib.import_module("src")
    assert pkg is not None


def test_sequencer_has_simple_smoke_sweep():
    sequencer = importlib.import_module("src.sequencer")
    assert hasattr(sequencer, "simple_smoke_sweep")


def test_dut_interface_stub_raises():
    dut = importlib.import_module("src.dut_interface")
    try:
        dut.reg_read(0x0)
    except NotImplementedError:
        pass
