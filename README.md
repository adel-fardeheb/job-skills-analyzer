# Job Skills Analyzer

Analyze the French job market and match CVs to job offers.

## Status

- [x] Phase 0: environment (WSL2, repo)
- [x] Phase 1: data collection from France Travail (about 6,400 offers, cleaning, duplicate flagging)
- [ ] Phase 2: skill extraction (dictionary baseline vs local LLM), in progress
- [ ] Phase 3: clustering and market analysis
- [ ] Phase 4: CV matching with skill-gap report
- [ ] Phase 5: Streamlit app and public demo

## Data

Offers come from the France Travail "Offres d'emploi" API, collected by ROME code and stored locally in PostgreSQL. Offers are deleted after 6 months. Only aggregated statistics are published, with links to the original offers; raw offer content is not redistributed.

Data quality notes:
- Near-identical offers are flagged, not deleted: same title/company/location key **and** description similarity of at least 90% (the key alone wrongly merged different offers).
- The API truncates some descriptions at 5,000 characters, so skills at the end of very long offers can be missed.
- Some descriptions contain inclusive-writing leftovers (for example `financier/ière`) and occasionally words glued together by the source.

## Evaluation method (Phase 2)

- 50 offers labeled by hand, one per ROME code plus a few extra, following written rules: only explicit, concrete skills (tools, technologies, methods, certifications, spoken languages), no soft skills.
- The dictionary is not tuned on these 50 offers, to keep the evaluation unbiased.
- Methods compared with precision, recall and F1: dictionary baseline vs local LLM (Ollama).

## Results

To be added at the end of Phase 2.

## Run

```bash
uv sync
cp .env.example .env        # fill in your own credentials, never commit .env
source .venv/bin/activate
python3 -m scripts.collect  # needs PostgreSQL and a France Travail API account
pytest -q
```

## Credits

- Job offers: France Travail open API.
- Skills taxonomy: ESCO, European Commission.