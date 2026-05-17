import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import (
    find_pdfs,
    prompt_selection,
    resolve_output_dir,
    convert_pdfs,
    combine_pdfs,
)


# --- find_pdfs ---

def test_find_pdfs_recursive(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (tmp_path / "a.pdf").touch()
    (sub / "b.pdf").touch()
    (tmp_path / "c.txt").touch()

    result = find_pdfs(tmp_path, recursive=True)
    assert len(result) == 2
    assert all(p.suffix == ".pdf" for p in result)


def test_find_pdfs_non_recursive(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (tmp_path / "a.pdf").touch()
    (sub / "b.pdf").touch()

    result = find_pdfs(tmp_path, recursive=False)
    assert result == [tmp_path / "a.pdf"]


def test_find_pdfs_empty(tmp_path):
    assert find_pdfs(tmp_path, recursive=True) == []


# --- prompt_selection ---

def test_prompt_selection_all(tmp_path):
    pdfs = [tmp_path / "a.pdf", tmp_path / "b.pdf"]
    assert prompt_selection.__doc__ is None  # no docstring expected
    # call directly with mocked input
    with patch("builtins.input", return_value="all"):
        result = prompt_selection(pdfs)
    assert result == pdfs


def test_prompt_selection_empty_input_defaults_to_all(tmp_path):
    pdfs = [tmp_path / "a.pdf", tmp_path / "b.pdf"]
    with patch("builtins.input", return_value=""):
        result = prompt_selection(pdfs)
    assert result == pdfs


def test_prompt_selection_indices(tmp_path):
    pdfs = [tmp_path / "a.pdf", tmp_path / "b.pdf", tmp_path / "c.pdf"]
    with patch("builtins.input", return_value="1, 3"):
        result = prompt_selection(pdfs)
    assert result == [pdfs[0], pdfs[2]]


def test_prompt_selection_ignores_invalid(tmp_path, capsys):
    pdfs = [tmp_path / "a.pdf"]
    with patch("builtins.input", return_value="99"):
        result = prompt_selection(pdfs)
    assert result == []
    assert "Ignoring invalid index" in capsys.readouterr().out


# --- resolve_output_dir ---

def test_resolve_output_dir_explicit(tmp_path):
    assert resolve_output_dir(tmp_path) == tmp_path


def test_resolve_output_dir_default():
    result = resolve_output_dir(None)
    assert result.parent == Path.home() / "Desktop"
    assert result.name.startswith("pdf_output_")


# --- convert_pdfs ---

def test_convert_pdfs(tmp_path):
    pdf = tmp_path / "sample.pdf"
    pdf.touch()
    out_dir = tmp_path / "out"

    mock_result = MagicMock()
    mock_result.text_content = "# Sample"
    mock_md = MagicMock()
    mock_md.convert.return_value = mock_result

    with patch("main.MarkItDown", return_value=mock_md):
        convert_pdfs([pdf], out_dir)

    out_file = out_dir / "sample.md"
    assert out_file.exists()
    assert out_file.read_text(encoding="utf-8") == "# Sample"


# --- combine_pdfs ---

def test_combine_pdfs(tmp_path):
    pdfs = [tmp_path / "a.pdf", tmp_path / "b.pdf"]
    for p in pdfs:
        p.touch()
    out_dir = tmp_path / "out"

    mock_writer = MagicMock()

    with patch("main.PdfWriter", return_value=mock_writer):
        combine_pdfs(pdfs, out_dir)

    assert mock_writer.append.call_count == 2
    mock_writer.write.assert_called_once()
