# Validation report: financial and geographic edition v7

## Source and data preservation

The package was revised from the attached `HUD-CDBG-DR-Fund-Dashboard-Hierarchical-main.zip`.

- All 128,382 financial records are retained.
- Every remaining financial, filter, reporting-quarter, grant/activity, and geographic field was compared with its corresponding original row. All match exactly.
- The two removed compact columns are the narrative availability flag and narrative linking ID. Rows now have 25 fields instead of 27.
- All five financial totals match the input to the cent.
- Filter dictionaries, metric definitions, quarter labels, geographic dictionaries, method dictionaries, and all three polygon payloads are identical to the source package.
- State, county, city/place, and urban-area mapped-row counts are unchanged.

## Removal and standalone verification

No narrative text chunks, narrative IDs/flags, narrative manifests, privacy QA tables, sanitizer script, or linked-narrative runtime sections are included. Both original narrative-only filtering paths and all narrative export/brief content have been removed. Documentation was revised and obsolete previews were removed.

The self-contained HTML was rebuilt from the cleaned files, rather than copied from the input. Its 13 compressed assets were decompressed and compared byte-for-byte with the source files. The embedded asset list is limited to the app, Plotly, bootstrap, seven financial chunks, and three geographic payloads. No external script or stylesheet is required by that HTML.

## Browser checks

Tests executed the actual rebuilt standalone HTML in Chromium using document-content loading. They covered:

- Explore & Compare as the default tab, two panels, 14 hierarchical filters, and six financial/geographic KPIs per panel.
- No narrative controls or narrative text in the rendered interface.
- National financial totals, geographic record counts, and independent panel selections.
- Grantee-to-project hierarchy and the explanatory no-metric state.
- Aggregate CSV generation: 1,446 national geography-quarter result rows, consistent column counts, no narrative fields.
- Funding PNG export; single-area and comparison reports; report CSV/PNG downloads; the image-based print window.
- Custom reporting ranges, reset controls, and a 390-pixel mobile viewport without horizontal page overflow.
- Standalone startup and report generation with network requests blocked.
- No JavaScript page errors, console errors, or narrative data requests during these tests.

**Testing limitation:** the managed test browser blocks direct HTTP/file navigation and does not provide WebGL. Native `file://` opening and a live GitHub Pages deployment were not executed here. Map tests exercised preserved geographic data, counts, and the existing WebGL-unavailable fallback, not interactive WebGL drawing. Use a WebGL-capable browser for the interactive maps. This revision preserves the existing map code and data apart from the required compact-column index updates.

## Build utilities and integrity

JavaScript syntax checks passed. A 40-row test-only financial/geographic sample exercised the updated static builder with no separate narrative file; it produced the expected 25-field financial rows and no narrative assets. Test sample inputs are not included in the release.

`docs/data_preservation_check.json`, `docs/package_validation_v7.json`, `docs/builder_smoke_v7.json`, and `docs/browser_validation_v7.json` record the checks. `PACKAGE_CONTENTS_SHA256.txt` lists hashes for the final package files. Run `python scripts/validate_static_package.py` after extracting the ZIP to verify the data, embedded assets, and hashes again.
