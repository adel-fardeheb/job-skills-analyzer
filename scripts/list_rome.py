import json
import re
from pathlib import Path

import httpx

from src import config
from src.ft_client import TokenManager

URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/referentiel/metiers"
OUT = Path("data/referentiel_metiers.json")
PATTERN = re.compile(
    r"informati|donn[ée]es|num[ée]rique|r[ée]seau|t[ée]l[ée]com|cyber|"
    r"logiciel|web|digital|statisti|syst[èe]mes? d",
    re.IGNORECASE,
)


def main():
    if not OUT.exists():
        tokens = TokenManager(
            config.require("FRANCE_TRAVAIL_CLIENT_ID"),
            config.require("FRANCE_TRAVAIL_CLIENT_SECRET"),
        )
        r = httpx.get(
            URL, headers={"Authorization": f"Bearer {tokens.get()}"}, timeout=30
        )
        r.raise_for_status()
        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text(r.text, encoding="utf-8")

    metiers = json.loads(OUT.read_text(encoding="utf-8"))
    print(len(metiers), "entries | first entry:", metiers[0])
    for m in metiers:
        if PATTERN.search(m["libelle"]):
            print(m["code"], "-", m["libelle"])


if __name__ == "__main__":
    main()