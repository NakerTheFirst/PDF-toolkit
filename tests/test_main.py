import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import (
    ask,
    find_pdfs,
    parse_selection,
    prompt_selection,
    resolve_output_dir,
    convert_pdfs,
    combine_pdfs,
)


# --- ask ---

def test_ask_returns_input():
    with patch("builtins.input", return_value="hello"):
        assert ask("prompt: ") == "hello"

def test_ask_quits_on_q():
    with patch("builtins.input", return_value="q"):
        with pytest.raises(SystemExit):
            ask("prompt: ")

def test_ask_quits_on_quit():
    with patch("builtins.input", return_value="quit"):
        with pytest.raises(SystemExit):
            ask("prompt: ")


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


# --- parse_selection ---

def test_parse_selection_plain_indices():
    assert parse_selection("1, 3", 5) == [1, 3]

def test_parse_selection_dot_indices():
    assert parse_selection("1., 2., 3.", 5) == [1, 2, 3]

def test_parse_selection_range():
    assert parse_selection("1-4", 5) == [1, 2, 3, 4]

def test_parse_selection_mixed_range_and_index():
    assert parse_selection("1-3, 5", 5) == [1, 2, 3, 5]

def test_parse_selection_exclusion():
    assert parse_selection("1-4, -2", 5) == [1, 3, 4]

def test_parse_selection_exclusion_from_spec():
    # Example from TODO: 1-4, 5, -2 => {1,2,3,4,5} - {2} = [1,3,4,5]
    assert parse_selection("1-4, 5, -2", 5) == [1, 3, 4, 5]

def test_parse_selection_single_index():
    assert parse_selection("3", 5) == [3]

def test_parse_selection_multiple_exclusions():
    # README example: 1-5, -2, -4 => [1,3,5]
    assert parse_selection("1-5, -2, -4", 5) == [1, 3, 5]

def test_parse_selection_mixed_dots_and_plain():
    assert parse_selection("1., 2, 3.", 5) == [1, 2, 3]

def test_parse_selection_duplicate_indices():
    # duplicates should be deduplicated via the set
    assert parse_selection("1, 1, 2", 5) == [1, 2]

def test_parse_selection_reverse_range_yields_empty():
    # range(4, 2) is empty — nothing added
    assert parse_selection("4-2", 5) == []

def test_parse_selection_exclusion_of_non_included():
    # -5 is excluded but was never in the included set — no effect
    assert parse_selection("1-3, -5", 5) == [1, 2, 3]

def test_parse_selection_exclusion_removes_everything():
    assert parse_selection("1, -1", 5) == []

def test_parse_selection_out_of_range_filtered():
    assert parse_selection("1, 99", 3) == [1]

def test_parse_selection_unrecognised_token(capsys):
    result = parse_selection("abc", 5)
    assert result == []
    assert "Ignoring unrecognised token" in capsys.readouterr().out


# --- prompt_selection ---

def test_prompt_selection_all(tmp_path):
    pdfs = [tmp_path / "a.pdf", tmp_path / "b.pdf"]
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


def test_prompt_selection_range(tmp_path):
    pdfs = [tmp_path / f"{c}.pdf" for c in "abcde"]
    with patch("builtins.input", return_value="2-4"):
        result = prompt_selection(pdfs)
    assert result == [pdfs[1], pdfs[2], pdfs[3]]


def test_prompt_selection_exclusion(tmp_path):
    pdfs = [tmp_path / f"{c}.pdf" for c in "abcd"]
    with patch("builtins.input", return_value="1-4, -2"):
        result = prompt_selection(pdfs)
    assert result == [pdfs[0], pdfs[2], pdfs[3]]


def test_prompt_selection_quit(tmp_path):
    pdfs = [tmp_path / "a.pdf"]
    with patch("builtins.input", return_value="q"):
        with pytest.raises(SystemExit):
            prompt_selection(pdfs)


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
