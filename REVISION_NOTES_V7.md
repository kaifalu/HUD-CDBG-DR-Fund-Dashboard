# Revision v7: remove narrative data and features

The input was `HUD-CDBG-DR-Fund-Dashboard-Hierarchical-main.zip`.

Removed:
- Narrative-only checkboxes and their effects on filtering in both dashboard modes.
- Linked-narrative sections, tables, highlights, address/redaction styling, and narrative loaders.
- Narrative content in decision briefs, takeaways, report CSV files, and analytical CSV files.
- Narrative-linked KPI cards, count/share fields, IDs, flags, manifests, metadata, source hashes, yearly data chunks, and privacy QA/crosswalk files.
- The old sanitizer, legacy verification files, and obsolete screenshots.
- The prior embedded narratives in the self-contained HTML, which has been rebuilt entirely from the cleaned site.

Preserved:
- Every financial record and all other financial/geographic fields, filter dictionaries, and map assets.
- Explore & Compare as the first/default tab, seven hierarchical filters per panel, all five financial measures, four geographic levels, and the existing footer/overview styling.
- Single-area/comparison Quick Reports and their report/aggregate/figure download functions.

The analytical KPI space is now used for Unique projects. The brief's removed narrative area is reclaimed for financial takeaways. Build scripts only publish financial/geographic fields and metadata. Asset requests are versioned to reduce stale-cache mismatches.

The 128,382 input financial rows were checked field-for-field after removing the two narrative-link columns. The five financial totals match to the cent. No new PII review of other source fields is implied by this change.
