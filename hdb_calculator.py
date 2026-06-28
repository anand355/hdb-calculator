# hdb_calculator.py
# A beginner-friendly CLI tool to explore Singapore HDB resale prices
# Data source: data.gov.sg (download CSV and place in the data/ folder)

import csv        # built-in: reads CSV files
import os         # built-in: handles file paths
import json       # built-in: saves/loads search history


# ──────────────────────────────────────────────
# STEP 1: LOAD DATA
# ──────────────────────────────────────────────

def load_data(filepath):
    """
    Reads the HDB CSV file and returns a list of records (dictionaries).
    Each record looks like:
      { 'month': '2023-01', 'town': 'TAMPINES', 'flat_type': '4 ROOM', ... }
    """
    records = []

    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        print("        Download the CSV from data.gov.sg and put it in the data/ folder.")
        return []

    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    print(f"[OK] Loaded {len(records)} records from {filepath}\n")
    return records


# ──────────────────────────────────────────────
# STEP 2: SEARCH / FILTER
# ──────────────────────────────────────────────

def search(records, town=None, flat_type=None, year=None):
    """
    Filters records by town, flat_type, and/or year.
    Any filter you leave as None is ignored (matches everything).
    """
    results = []

    for record in records:
        if town and record['town'].upper() != town.upper():
            continue
        if flat_type and record['flat_type'].upper() != flat_type.upper():
            continue
        if year and not record['month'].startswith(year):
            continue
        results.append(record)

    return results


# ──────────────────────────────────────────────
# STEP 3: CALCULATE STATS
# ──────────────────────────────────────────────

def calculate_stats(results):
    """
    Given a list of matching records, compute price statistics.
    Returns a dict with average, min, max, and count.
    """
    if not results:
        return None

    prices = [int(r['resale_price']) for r in results]

    return {
        'count':   len(prices),
        'average': sum(prices) // len(prices),
        'minimum': min(prices),
        'maximum': max(prices),
    }


# ──────────────────────────────────────────────
# STEP 4: DISPLAY RESULTS
# ──────────────────────────────────────────────

def display_results(results, stats):
    """Prints the search results and summary stats to the terminal."""

    if not results:
        print("No matching records found. Try different search terms.\n")
        return

    print("-" * 65)
    print(f"{'Month':<10} {'Town':<16} {'Type':<10} {'Storey':<14} {'Price':>12}")
    print("-" * 65)

    shown = results[:20]
    for r in shown:
        print(
            f"{r['month']:<10} "
            f"{r['town']:<16} "
            f"{r['flat_type']:<10} "
            f"{r['storey_range']:<14} "
            f"S${int(r['resale_price']):>10,}"
        )

    if len(results) > 20:
        print(f"  ... and {len(results) - 20} more records (showing first 20)")

    print("-" * 65)
    print(f"  Results found : {stats['count']}")
    print(f"  Average price : S${stats['average']:,}")
    print(f"  Lowest price  : S${stats['minimum']:,}")
    print(f"  Highest price : S${stats['maximum']:,}")
    print("-" * 65)
    print()


# ──────────────────────────────────────────────
# STEP 5: SEARCH HISTORY
# ──────────────────────────────────────────────

HISTORY_FILE = "data/search_history.json"

def save_to_history(town, flat_type, year, stats):
    """Appends a search + its results to a JSON history file."""

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    else:
        history = []

    entry = {
        "town":      town or "any",
        "flat_type": flat_type or "any",
        "year":      year or "any",
        "count":     stats['count'],
        "average":   stats['average'],
    }
    history.append(entry)

    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def show_history():
    """Prints past searches from the history file."""
    if not os.path.exists(HISTORY_FILE):
        print("No search history yet.\n")
        return

    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)

    if not history:
        print("No search history yet.\n")
        return

    print("\n--- Your past searches ---")
    for i, entry in enumerate(history[-10:], 1):
        print(
            f"  {i}. {entry['town']} | {entry['flat_type']} | {entry['year']} "
            f"→ {entry['count']} results, avg S${entry['average']:,}"
        )
    print()


# ──────────────────────────────────────────────
# STEP 6: SHOW AVAILABLE OPTIONS
# ──────────────────────────────────────────────

def show_available(records, field):
    """Prints all unique values for a given field."""
    values = sorted(set(r[field] for r in records))
    print(f"\nAvailable {field.replace('_', ' ')}s:")
    for v in values:
        print(f"  - {v}")
    print()


# ──────────────────────────────────────────────
# STEP 7: MAIN MENU
# ──────────────────────────────────────────────

def main():
    print("=" * 65)
    print("   HDB Resale Price Calculator — Singapore")
    print("   Data source: data.gov.sg")
    print("=" * 65)

    data_file = "data/sample_hdb.csv"

    records = load_data(data_file)
    if not records:
        return

    while True:
        print("What would you like to do?")
        print("  1. Search resale prices")
        print("  2. View search history")
        print("  3. See available towns")
        print("  4. See available flat types")
        print("  5. Quit")

        choice = input("\nEnter choice (1-5): ").strip()
        print()

        if choice == "1":
            print("Leave any field blank to match everything.\n")
            town      = input("Town (e.g. TAMPINES, ANG MO KIO): ").strip().upper() or None
            flat_type = input("Flat type (e.g. 4 ROOM, 5 ROOM, 3 ROOM): ").strip().upper() or None
            year      = input("Year (e.g. 2023, 2022): ").strip() or None

            print()
            results = search(records, town=town, flat_type=flat_type, year=year)
            stats   = calculate_stats(results)

            display_results(results, stats)

            if stats:
                save_to_history(town, flat_type, year, stats)
                print("[Saved to history]\n")

        elif choice == "2":
            show_history()

        elif choice == "3":
            show_available(records, 'town')

        elif choice == "4":
            show_available(records, 'flat_type')

        elif choice == "5":
            print("Bye! Happy flat hunting.")
            break

        else:
            print("Invalid choice, please enter 1–5.\n")


if __name__ == "__main__":
    main()