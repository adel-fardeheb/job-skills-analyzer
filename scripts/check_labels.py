import json
from collections import Counter
from pathlib import Path

from src.labeling import validate_labels

PATH = Path("data/labels/labeled_set.json")
WATCHED = ["gestion de projet", "bioinformatique"]


def main():
    entries = json.loads(PATH.read_text(encoding="utf-8"))

    problems = validate_labels(entries)
    print(f"{len(entries)} offers, {len(problems)} problems")
    for p in problems:
        print("  -", p)

    counts = [len(e["skills"]) for e in entries]
    print(f"skills per offer: mean {sum(counts) / len(counts):.1f}, "
          f"min {min(counts)}, max {max(counts)}, empty: {counts.count(0)}")

    freq = Counter(s for e in entries for s in e["skills"])
    print("most frequent:", freq.most_common(10))

    for term in WATCHED:
        missing = [
            e["source_id"]
            for e in entries
            if term in e["description"].lower()
            and not any(term in s for s in e["skills"])
        ]
        print(f"'{term}' in text but not labeled: {missing}")


if __name__ == "__main__":
    main()