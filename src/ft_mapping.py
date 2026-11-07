from datetime import datetime
from src.cleaning import clean_text, make_dedup_key

def _dt(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def ft_to_row(offer, collected_at):
    """Map one France Travail offer (dict) to a row of the offers table."""
    return {
        "source": "france_travail",
        "source_id": offer["id"],
        "title": offer.get("intitule"),
        "company": (offer.get("entreprise") or {}).get("nom"),
        "location": (offer.get("lieuTravail") or {}).get("libelle"),
        "description": clean_text(offer.get("description")),
        "url": (offer.get("origineOffre") or {}).get("urlOrigine"),
        "contract_type": offer.get("typeContrat"),
        "rome_code": offer.get("romeCode"),
        "rome_label": offer.get("romeLibelle"),
        "experience": offer.get("experienceLibelle"),
        "source_skills": offer.get("competences"),
        "created_at": _dt(offer.get("dateCreation")),
        "updated_at": _dt(offer.get("dateActualisation")),
        "collected_at": collected_at,
        "dedup_key": make_dedup_key(
            offer.get("intitule"),
            (offer.get("entreprise") or {}).get("nom"),
            (offer.get("lieuTravail") or {}).get("libelle"),
        ),
    }