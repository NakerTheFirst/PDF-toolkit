# PDF Toolkit

CLI tool for batch PDF-to-Markdown conversion and PDF merging, with interactive file selection.

## Usage

```bash
pip install -r requirements.txt
```

### Interactive mode

```bash
python src/main.py
```

Prompts for directory, operation, and file selection in sequence. Type `q` at any prompt to quit.

### With arguments

```bash
# Specify a directory to scan (recursive by default)
python src/main.py ./docs

# Non-recursive scan
python src/main.py ./docs --non-recursive

# Custom output directory
python src/main.py ./docs --output ./out

# All flags combined
python src/main.py ./docs --non-recursive --output ./out
```

Output defaults to `~/Desktop/pdf_output_HH-MM/` when `--output` is omitted.

## Selecting files

After PDFs are discovered and listed, you are prompted to choose which to include.

```
Found 5 PDF(s):
  1. annual-report.pdf
  2. appendix-a.pdf
  3. appendix-b.pdf
  4. appendix-c.pdf
  5. summary.pdf
```

| Input | Meaning | Selects |
|---|---|---|
| *(empty)* or `all` | every file | 1 2 3 4 5 |
| `1, 3, 5` | specific indices | 1 3 5 |
| `1., 2., 3.` | indices with trailing dot | 1 2 3 |
| `2-4` | inclusive range | 2 3 4 |
| `1-3, 5` | range and individual | 1 2 3 5 |
| `1-4, -3` | range minus exclusion | 1 2 4 |
| `1-5, -2, -4` | range minus multiple exclusions | 1 3 5 |

## Structure

```
PDF-toolkit/
├── src/
│   └── main.py          # single-file CLI entry point
├── tests/
│   └── test_main.py     # test suite
├── requirements.txt
└── pyproject.toml
```

## Possible extensions
- Scrape PDFs from a cloud storage (Google Drive, Moodle/E-learning resources)
