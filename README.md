# BuildWise AI — Streamlit prototype

## Features
- Exactly three project inputs: location, plot area, building type.
- Candidate floor options and user selection.
- Separate schematic 2D architectural plan for every selected floor.
- Labelled concept RCC grid with columns (C), beams (B), slab panels (S).
- Selectable beam, column, slab or foundation IDs with section sketches and indicative quantity tables.
- Illustrative beam shear-force and bending-moment diagrams.
- Whole-building area-factor quantity/cost estimate and downloadable text report.

## Run locally
```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Deploy with GitHub and Streamlit Community Cloud
1. Upload `app.py`, `requirements.txt`, and `README.md` to the repository root.
2. In Streamlit Community Cloud, choose the repository, branch, and `app.py` as the main file.
3. Deploy and test the resulting app.

## Important limitations
This is an educational concept prototype, not construction-ready design software. Plot geometry, setbacks, coverage, loading, member dimensions, reinforcement factors, and cost rates are illustrative assumptions. It does not verify local planning rules, site-specific soil bearing capacity, full building analysis, reinforcement design, or compliance with current structural standards. The section diagrams show schematic reinforcement markers only. All drawings and calculations must be validated by qualified professionals before real-world use.
