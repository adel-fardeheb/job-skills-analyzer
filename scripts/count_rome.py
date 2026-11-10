import csv
import json
import logging
import sys
from datetime import date
from pathlib import Path

from src import config
from src.ft_client import TokenManager
from src.ft_search import OffersSearch
from src.request_budget import RequestBudget

REFERENTIEL = Path("data/referentiel_metiers.json")
OUT = Path("data/counts_rome_national.csv")

CODES = [
    # data and AI
    "M1405", "M1811", "M1889", "M1419", "M1423", "M1872", "M1851", "M1824",
    "M1414", "K2403", "K2408", "H1215", "M1822",
    # development
    "M1805", "M1861", "M1855", "M1836", "M1841", "M1818", "M1848", "M1852",
    "M1853", "M1815", "M1892",
    # systems, networks, security
    "M1801", "M1802", "M1810", "M1839", "M1884", "M1812", "M1856", "M1882",
    "M1883", "M1819", "M1817", "M1868", "M1894",
    # management and consulting
    "M1803", "M1867", "M1806", "M1881", "M1870",
    # adjacent
    "C1202", "M1201", "K2402",
]


def main():
    logging.basicConfig(level=logging.WARNING)
    labels = {
        m["code"]: m["libelle"]
        for m in json.loads(REFERENTIEL.read_text(encoding="utf-8"))
    }
    codes = sys.argv[1:] or CODES   #Allows you to override the hardcoded list
    today = date.today().isoformat()

    done = set()
    if OUT.exists():
        with OUT.open(encoding="utf-8") as f:
            done = {r["code"] for r in csv.DictReader(f) if r["date"] == today}
    todo = [c for c in codes if c not in done]

    budget = RequestBudget()
    print(f"{len(todo)} codes to count, {budget.used()} requests used in the last 7 days")
    search = OffersSearch(
        TokenManager(
            config.require("FRANCE_TRAVAIL_CLIENT_ID"),
            config.require("FRANCE_TRAVAIL_CLIENT_SECRET"),
        ),
        budget=budget,
    )

    new_file = not OUT.exists()
    with OUT.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["date", "code", "label", "total"])
        for code in todo:
            _, total = search.fetch_page({"codeROME": code}, 0, 0)
            label = labels.get(code, "?")
            writer.writerow([today, code, label, total])
            f.flush()  # keep what is counted even if the run stops midway
            print(f"{code} {total:>6}  {label}")


if __name__ == "__main__":
    main()