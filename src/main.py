import argparse
import re
from datetime import datetime
from pathlib import Path

from markitdown import MarkItDown
from pypdf import PdfWriter


def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch PDF-to-Markdown conversion and PDF merging."
    )
    parser.add_argument(
        "search_dir",
        nargs="?",
        type=Path,
        help="Directory to scan for PDFs. Prompted interactively if omitted.",
    )
    parser.add_argument(
        "--non-recursive",
        action="store_true",
        help="Search only the specified directory, skip subdirectories.",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output directory. Created if missing. Default: ~/Desktop/pdf_output_HH-MM/.",
    )
    return parser.parse_args()


def resolve_output_dir(output: Path | None) -> Path:
    if output is not None:
        return output
    timestamp = datetime.now().strftime("%H-%M")
    return Path.home() / "Desktop" / f"pdf_output_{timestamp}"


_QUIT_SIGNALS = {"q", "quit", "exit"}


def ask(prompt: str) -> str:
    raw = input(prompt).strip()
    if raw.lower() in _QUIT_SIGNALS:
        print("Quitting.")
        raise SystemExit(0)
    return raw


def prompt_search_dir() -> Path:
    return Path(ask("Enter directory to scan for PDFs: "))


def prompt_operation() -> str:
    print("\nWhat would you like to do?")
    print("  1. Convert PDFs to Markdown")
    print("  2. Combine PDFs into one file")
    while True:
        choice = ask("Choose (1/2): ")
        if choice in ("1", "2"):
            return "convert" if choice == "1" else "combine"
        print("Please enter 1 or 2.")


def parse_selection(raw: str, count: int) -> list[int]:
    """Parse a selection string into a sorted list of valid 1-based indices.

    Supported tokens (comma-separated):
      1, 2, 3    plain indices
      1., 2.     indices with trailing dot
      1-3        inclusive range
      -2         exclude index 2 from previously included indices
    """
    included: set[int] = set()
    excluded: set[int] = set()
    for token in raw.split(","):
        token = token.strip().rstrip(".")
        if not token:
            continue
        if re.fullmatch(r"-\d+", token):
            excluded.add(int(token[1:]))
        elif re.fullmatch(r"\d+-\d+", token):
            a, b = (int(x) for x in token.split("-"))
            included.update(range(a, b + 1))
        elif re.fullmatch(r"\d+", token):
            included.add(int(token))
        else:
            print(f"Ignoring unrecognised token: {token!r}")
    return sorted(i for i in included if 1 <= i <= count and i not in excluded)


def prompt_selection(pdfs: list[Path]) -> list[Path]:
    raw = ask("\nWhich PDFs to include? (indices/ranges/exclusions or 'all') [all]: ")
    if not raw or raw.lower() == "all":
        return list(pdfs)
    indices = parse_selection(raw, len(pdfs))
    return [pdfs[i - 1] for i in indices]


def convert_pdfs(pdfs: list[Path], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    md = MarkItDown()
    for pdf in pdfs:
        result = md.convert(str(pdf))
        out_path = output_dir / (pdf.stem + ".md")
        out_path.write_text(result.text_content, encoding="utf-8")
        print(f"  Converted: {out_path}")


def combine_pdfs(pdfs: list[Path], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    for pdf in pdfs:
        writer.append(str(pdf))
    out_path = output_dir / "combined.pdf"
    with out_path.open("wb") as f:
        writer.write(f)
    print(f"  Combined: {out_path}")


def find_pdfs(search_dir: Path, recursive: bool) -> list[Path]:
    pattern = "**/*.pdf" if recursive else "*.pdf"
    return sorted(search_dir.glob(pattern))


def display_pdfs(pdfs: list[Path]) -> None:
    for i, pdf in enumerate(pdfs, 1):
        print(f"  {i}. {pdf.name}")


def main():
    args = parse_args()
    search_dir = args.search_dir or prompt_search_dir()
    output_dir = resolve_output_dir(args.output)

    pdfs = find_pdfs(search_dir, recursive=not args.non_recursive)
    if not pdfs:
        print("No PDFs found.")
        return

    print(f"\nFound {len(pdfs)} PDF(s):")
    display_pdfs(pdfs)

    operation = prompt_operation()
    selected = prompt_selection(pdfs)
    if not selected:
        print("No valid PDFs selected.")
        return

    if operation == "convert":
        convert_pdfs(selected, output_dir)
    else:
        combine_pdfs(selected, output_dir)


if __name__ == "__main__":
    main()
