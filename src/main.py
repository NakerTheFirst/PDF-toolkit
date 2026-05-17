import argparse
from datetime import datetime
from pathlib import Path


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


def prompt_search_dir() -> Path:
    raw = input("Enter directory to scan for PDFs: ").strip()
    return Path(raw)


def prompt_operation() -> str:
    print("\nWhat would you like to do?")
    print("  1. Convert PDFs to Markdown")
    print("  2. Combine PDFs into one file")
    while True:
        choice = input("Choose (1/2): ").strip()
        if choice in ("1", "2"):
            return "convert" if choice == "1" else "combine"
        print("Please enter 1 or 2.")


def prompt_selection(pdfs: list[Path]) -> list[Path]:
    raw = input("\nWhich PDFs to include? (comma-separated indices or 'all') [all]: ").strip()
    if not raw or raw.lower() == "all":
        return pdfs
    indices = [s.strip() for s in raw.split(",")]
    selected = []
    for idx in indices:
        if idx.isdigit() and 1 <= int(idx) <= len(pdfs):
            selected.append(pdfs[int(idx) - 1])
        else:
            print(f"Ignoring invalid index: {idx!r}")
    return selected


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


if __name__ == "__main__":
    main()
