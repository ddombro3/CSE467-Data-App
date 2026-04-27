"""
main.py

LLM Privacy Data Extractor.

Default behavior:
    Shows an interactive CLI menu.
    User can select URLs from config/sources.csv or add custom URLs.
    Scrapes selected URLs.
    Saves raw text into data/raw/.
    Extracts privacy-related keyword matches.
    Saves results into data/output/.
"""

from pathlib import Path
import argparse

from extractor import extract_privacy_data
from file_utils import read_sources_csv, save_results, save_summary
from scraper import scrape_source_to_raw_file


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"

SOURCES_CSV = CONFIG_DIR / "sources.csv"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract privacy-related data from LLM platform privacy policies and documentation."
    )

    parser.add_argument(
        "--url",
        help="Single privacy policy or documentation URL to scrape."
    )

    parser.add_argument(
        "--platform",
        default="Unknown Platform",
        help="Platform name for single URL mode. Example: Claude"
    )

    parser.add_argument(
        "--source-name",
        default="Unknown Source",
        help='Source name for single URL mode. Example: "Anthropic Privacy Policy"'
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all URLs from config/sources.csv without showing the interactive menu."
    )

    return parser.parse_args()


def build_sources_from_args(args):

    if args.url:
        return [
            {
                "platform": args.platform,
                "source_name": args.source_name,
                "url": args.url,
            }
        ]

    return None


def print_source_menu(sources):

    print()
    print("Available saved sources:")
    print("-" * 80)

    for index, source in enumerate(sources, start=1):
        platform = source["platform"]
        source_name = source["source_name"]
        url = source["url"]

        print(f"[{index}] {platform} - {source_name}")
        print(f"    {url}")

    print("-" * 80)
    print()


def parse_selection(selection_text, max_number):

    selection_text = selection_text.strip().lower()

    if selection_text == "all":
        return list(range(max_number))

    if selection_text in {"none", "n", "no", ""}:
        return []

    selected_indexes = set()

    parts = selection_text.split(",")

    for part in parts:
        part = part.strip()

        if not part:
            continue

        if "-" in part:
            start_text, end_text = part.split("-", 1)

            if not start_text.strip().isdigit() or not end_text.strip().isdigit():
                print(f"Invalid range ignored: {part}")
                continue

            start = int(start_text.strip())
            end = int(end_text.strip())

            if start > end:
                print(f"Invalid range ignored: {part}")
                continue

            for number in range(start, end + 1):
                if 1 <= number <= max_number:
                    selected_indexes.add(number - 1)
                else:
                    print(f"Number out of range ignored: {number}")

        else:
            if not part.isdigit():
                print(f"Invalid selection ignored: {part}")
                continue

            number = int(part)

            if 1 <= number <= max_number:
                selected_indexes.add(number - 1)
            else:
                print(f"Number out of range ignored: {number}")

    return sorted(selected_indexes)


def ask_yes_no(prompt):

    while True:
        answer = input(prompt).strip().lower()

        if answer in {"y", "yes"}:
            return True

        if answer in {"n", "no"}:
            return False

        print("Please enter y or n.")


def collect_custom_sources():

    custom_sources = []

    print()
    print("Custom URL entry")
    print()

    while True:
        url = input("Enter custom URL: ").strip()

        if not url:
            print("No URL entered. Returning to source selection.")
            break

        platform = input("Platform name, example Claude/OpenAI/Gemini/Copilot: ").strip()
        source_name = input("Source name, example Privacy Policy/API Docs: ").strip()

        if not platform:
            platform = "Custom Platform"

        if not source_name:
            source_name = "Custom Source"

        custom_sources.append({
            "platform": platform,
            "source_name": source_name,
            "url": url,
        })

        print("Custom source added.")
        print()

        if not ask_yes_no("Add another custom URL? (y/n): "):
            break

        print()

    return custom_sources


def interactive_select_sources(saved_sources):

    print_source_menu(saved_sources)

    print("Select sources to scrape.")
    print("Examples:")
    print("  1")
    print("  1,3,5")
    print("  1-4")
    print("  1,3-5")
    print("  all")
    print("  none")
    print()

    selection_text = input("Enter your selection: ")

    selected_indexes = parse_selection(
        selection_text=selection_text,
        max_number=len(saved_sources),
    )

    selected_sources = [saved_sources[index] for index in selected_indexes]

    print()
    print(f"Saved sources selected: {len(selected_sources)}")

    if ask_yes_no("Add custom URL(s)? (y/n): "):
        custom_sources = collect_custom_sources()
        selected_sources.extend(custom_sources)

    print()
    print("Final selected sources:")
    print("-" * 80)

    if not selected_sources:
        print("No sources selected.")
    else:
        for index, source in enumerate(selected_sources, start=1):
            print(f"[{index}] {source['platform']} - {source['source_name']}")
            print(f"    {source['url']}")

    print("-" * 80)
    print()

    if not selected_sources:
        return []

    if not ask_yes_no("Continue with these sources? (y/n): "):
        print("Canceled by user.")
        return []

    return selected_sources


def run_extraction(sources):

    all_results = []

    for source in sources:
        try:
            raw_file_path, text = scrape_source_to_raw_file(
                source=source,
                raw_data_dir=RAW_DATA_DIR,
            )
        except Exception as error:
            print()
            print(f"Failed to scrape source: {source.get('source_name')}")
            print(f"URL: {source.get('url')}")
            print(f"Error: {error}")
            print("Skipping this source.")
            print()
            continue

        results = extract_privacy_data(
            platform=source["platform"],
            source_name=source["source_name"],
            source_url=source["url"],
            source_file=str(raw_file_path.relative_to(PROJECT_ROOT)),
            text=text,
        )

        print(f"Matches found: {len(results)}")
        print()

        all_results.extend(results)

    csv_path = OUTPUT_DIR / "extracted_privacy_data.csv"
    excel_path = OUTPUT_DIR / "extracted_privacy_data.xlsx"

    summary_csv_path = OUTPUT_DIR / "extraction_summary.csv"
    summary_excel_path = OUTPUT_DIR / "extraction_summary.xlsx"

    df = save_results(
        results=all_results,
        csv_path=csv_path,
        excel_path=excel_path,
    )

    summary_df = save_summary(
        df=df,
        csv_path=summary_csv_path,
        excel_path=summary_excel_path,
    )

    print("Extraction complete.")
    print(f"Total rows extracted: {len(df)}")
    print(f"Detailed CSV saved to: {csv_path}")
    print(f"Detailed Excel saved to: {excel_path}")
    print(f"Summary CSV saved to: {summary_csv_path}")
    print(f"Summary Excel saved to: {summary_excel_path}")
    print(f"Summary rows: {len(summary_df)}")


def main():
    args = parse_args()

    cli_sources = build_sources_from_args(args)

    if cli_sources:
        print("Running in single URL mode.")
        sources = cli_sources

    else:
        print(f"Reading saved source database from: {SOURCES_CSV}")
        saved_sources = read_sources_csv(SOURCES_CSV)

        if args.all:
            print("Running all saved sources.")
            sources = saved_sources
        else:
            sources = interactive_select_sources(saved_sources)

    if not sources:
        print("No sources to process. Exiting.")
        return

    run_extraction(sources)


if __name__ == "__main__":
    main()