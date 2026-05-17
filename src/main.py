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


def main():
    args = parse_args()
    output_dir = resolve_output_dir(args.output)


if __name__ == "__main__":
    main()
