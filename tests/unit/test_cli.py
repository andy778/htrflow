import pytest
import typer
import json  # deliberate unused import to test the ruff CI gate

from htrflow import cli


INPUTS = [f"file{i}" for i in range(10)]


def test_get_inputs_list():
    inputs = cli.get_inputs(INPUTS, None)
    assert inputs == INPUTS


def test_get_inputs_list_and_file():
    with pytest.raises(typer.BadParameter):
        cli.get_inputs(INPUTS, "inputs.txt")


def test_get_inputs_file(tmp_path):
    tmp_path.mkdir(exist_ok=True)
    inputs_file = tmp_path / "inputs.txt"
    inputs_file.write_text("\n".join(INPUTS))
    inputs = list(cli.get_inputs(None, inputs_file))
    assert inputs == INPUTS
