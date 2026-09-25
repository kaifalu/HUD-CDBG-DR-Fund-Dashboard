# CDBG-DR Fund Dashboard
## Financial and geographic edition · v7

This is a complete, root-ready static GitHub Pages website. It preserves Explore & Compare, Quick Report, financial charts, geographic analysis, and aggregate downloads. Explore & Compare opens first.

### What is included

- Two independent comparison panels and seven linked filters per panel.
- State, county/county-equivalent, city/place point, and 2010 Census urban-area views.
- Five financial measures and quarterly/cumulative net trends.
- Single-area and two-scenario one-page decision briefs with a map, four indicators, a trend, a top-five ranking, and calculated takeaways.
- Aggregate CSV, map/funding-plot PNG, report PNG, and Print / Save as PDF controls.
- A self-contained `HUD-CDBG-DR-Fund-Dashboard-Hierarchical.html` containing the same updated application.
- Local Plotly assets, source code, build scripts, user instructions, and validation tools.

### Update an existing repository

Extract this ZIP and replace the previous website files with its contents. Put `index.html`, `.nojekyll`, `assets/`, and `data/` directly in the repository root, not inside another folder.

**Do not only upload over the previous files.** Delete the old `data/narratives/` and `privacy/` folders, `scripts/sanitize_narratives.py`, older self-contained HTML copies, and obsolete screenshots/documentation. An upload does not automatically delete files that are absent from the new ZIP. This package does not change already published copies, Git history, releases, or external caches.

Keep the existing Pages setting: `main` branch, `/(root)` folder. No server, database, or Python runtime is needed for the published dashboard. The included `GITHUB_PAGES_SETUP.md` explains file placement. The application uses versioned asset requests to reduce mixed-version browser caches; perform a hard refresh after deployment.

### Open locally

For the complete multi-file site, run `python -m http.server 8000` in the extracted folder and open `http://localhost:8000/`. Alternatively use `run_local.bat` or `run_local.sh`.

For direct file opening, double-click `HUD-CDBG-DR-Fund-Dashboard-Hierarchical.html`. It embeds the application, financial data, and geographic assets, and does not need the other folders.

### Data preservation

All 128,382 financial records, seven filter dictionaries, five financial measures, geographic assignments, and geographic boundary/point assets have been preserved. The compact row schema has 25 fields. Narrative text, availability flags, linking identifiers, data chunks, related metadata, filtering controls, report sections, and exports have been removed rather than merely hidden.

Financial project/activity titles and geographic labels remain as supplied. This is a removal of the narrative dataset, not a new privacy review of other source fields.

### Developer checks

Run `python scripts/validate_static_package.py` from the extracted folder. Run `python scripts/build_self_contained.py` after editing the multi-file application to regenerate the standalone HTML. `build_static_data.py` rebuilds finance/geography chunks from prepared financial and geographic inputs; these original upstream inputs are not included in this deployment ZIP.

See `USER_GUIDE.md`, `DATA_METHODS.md`, `REVISION_NOTES_V7.md`, and `VALIDATION_REPORT.md` for further detail.
