# Data and interpretation

## Financial records

The supplied application includes 128,382 quarter-level financial records. The source metadata report 130,605 financial rows, of which 2,223 rows lacking a valid reporting quarter were excluded upstream. This revision does not re-filter or drop any of the application's financial records.

The five original QPR measures are funds obligated, funds expended, grant disbursed, activity program income disbursed, and activity program income received. All five measures, every record's financial/geographic values, and all filter dictionaries are unchanged from the attached input package.

The reporting-quarter range in the package is 2002 Q3 through 2025 Q2. The Year dropdown is a separate disaster/appropriation-year field. Quarterly values are source-period net transactions; cumulative displays sum the selected quarters chronologically. Values are not inflation-adjusted or normalized by population, damages, or grant size.

## Geography

State assignment uses Grantee State directly. County/county-equivalent matching combines direct county text and matched city/place primary counties. City/place markers use the supplied city gazetteer's coordinates, not municipal polygons. The 2010 Census urban-area view is a secondary statistical geography, not a city-limit map.

The preserved record-level coverage is 100.00% for states, 65.68% for enhanced counties, 37.39% for city/place points, and 29.69% for urban areas. At each level, records without a match are excluded from the map and associated analysis. Coverage reports the match share among records satisfying nongeographic filters before choosing a particular mapped location.

## Counts and aggregation

Grant and activity counts use the encoded grant and grant-plus-activity keys. Project counts/rankings use the source project-title dictionary. Aggregate exports group displayed records by geography and QPR quarter, with distinct counts and quarterly/cumulative net measures. Counts in different quarter groups must not be summed to derive distinct grants, projects, or activities across the full period.

## Compact data format

Each financial record now has 25 fields. `data/bootstrap.js` declares the column indices and dictionaries; `data/rows/rows_*.js` stores the records. No original financial records have been removed. See `data/STATIC_DATA_SCHEMA.md` for the field order and `docs/data_preservation_check.json` for the input-versus-output check.

This dashboard is an exploratory research tool, not an official HUD accounting, compliance, or recovery-outcome determination. Supporting research requires source verification and appropriate program context.
