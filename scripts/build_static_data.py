#!/usr/bin/env python3
"""Build compact, browser-only data assets for the GitHub Pages dashboard.

The generated assets are ordinary JavaScript files. They can be served directly
from a GitHub Pages branch without Python, Node.js, a database, or a build step.

Example
-------
python scripts/build_static_data.py \
  --processed-dir ../disaster_dashboard_render/data/processed \
  --site-dir .
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

FILTER_COLUMNS = [
    ("Year", "years"),
    ("Disaster Type", "disasterTypes"),
    ("Grantee", "grantees"),
    ("Project Title", "projects"),
    ("Activity Responsible Org", "organizations"),
    ("Activity Type", "activityTypes"),
    ("Activity Title", "activityTitles"),
]

METRIC_COLUMNS = [
    "QPR Funds Obligated $",
    "QPR Fund Expended $",
    "QPR Grant Disbursed $",
    "QPR Activity Program Income Disbursed $",
    "QPR Activity Program Income Received $",
]

GEO_SPECS = {
    "state": {
        "id_col": "state_fips",
        "name_col": "state_name",
        "source_geojson": "state.geojson",
    },
    "county": {
        "id_col": "county_geoid",
        "name_col": "county_display_name",
        "source_geojson": "county.geojson",
    },
    "city": {
        "id_col": "city_id",
        "name_col": "city_display_name",
        "lat_col": "city_lat",
        "lon_col": "city_lng",
    },
    "urban": {
        "id_col": "ua_geoid",
        "name_col": "ua_name",
        "source_geojson": "urban_area.geojson",
    },
}

COLUMN_INDEX = {
    "year": 0,
    "disasterType": 1,
    "grantee": 2,
    "project": 3,
    "organization": 4,
    "activityType": 5,
    "activityTitle": 6,
    "quarter": 7,
    "grantCode": 8,
    "activityCode": 9,
    "state": 10,
    "county": 11,
    "city": 12,
    "urban": 13,
    "countyMethod": 14,
    "countyConfidence": 15,
    "cityMethod": 16,
    "cityConfidence": 17,
    "urbanMethod": 18,
    "urbanConfidence": 19,
    "metricStart": 20,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--processed-dir",
        type=Path,
        required=True,
        help="Directory containing finance_processed.csv.gz, metadata.json, and GeoJSON files.",
    )
    parser.add_argument(
        "--site-dir",
        type=Path,
        required=True,
        help="Root of the static GitHub Pages site.",
    )
    parser.add_argument(
        "--rows-per-chunk",
        type=int,
        default=20000,
        help="Maximum finance rows per JavaScript chunk.",
    )
    return parser.parse_args()


def clean_string(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text if text else None


def sorted_unique(series: pd.Series, *, year: bool = False) -> list[str]:
    values = {clean_string(value) for value in series.tolist()}
    values.discard(None)
    if year:
        return sorted(values, key=lambda value: (int(value) if value.isdigit() else 999999, value))
    return sorted(values, key=lambda value: value.casefold())


def encode_values(series: pd.Series, values: list[str]) -> np.ndarray:
    lookup = {value: index for index, value in enumerate(values)}
    return np.array([lookup.get(clean_string(value), -1) for value in series.tolist()], dtype=np.int32)


def aligned_geography(frame: pd.DataFrame, spec: dict[str, str]) -> tuple[dict[str, Any], np.ndarray]:
    id_col = spec["id_col"]
    name_col = spec["name_col"]
    rows = frame[[id_col, name_col] + [column for column in (spec.get("lat_col"), spec.get("lon_col")) if column]].copy()
    rows[id_col] = rows[id_col].map(clean_string)
    rows[name_col] = rows[name_col].map(clean_string)
    rows = rows[rows[id_col].notna()].drop_duplicates(id_col)
    rows = rows.sort_values(name_col, key=lambda values: values.fillna("").str.casefold())
    ids = rows[id_col].astype(str).tolist()
    names = rows[name_col].fillna(rows[id_col]).astype(str).tolist()
    lookup = {value: index for index, value in enumerate(ids)}
    codes = np.array([lookup.get(clean_string(value), -1) for value in frame[id_col].tolist()], dtype=np.int32)
    output: dict[str, Any] = {"ids": ids, "names": names}
    if spec.get("lat_col"):
        output["lat"] = pd.to_numeric(rows[spec["lat_col"]], errors="coerce").round(6).where(lambda s: s.notna(), None).tolist()
        output["lon"] = pd.to_numeric(rows[spec["lon_col"]], errors="coerce").round(6).where(lambda s: s.notna(), None).tolist()
    return output, codes


def factor_codes(series: pd.Series) -> np.ndarray:
    normalized = series.map(lambda value: clean_string(value) or "")
    codes, _ = pd.factorize(normalized, sort=True)
    return codes.astype(np.int32)


def write_js_assignment(path: Path, expression: str, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    path.write_text(f"{expression}{serialized};\n", encoding="utf-8")


def sanitize_json(value: Any) -> Any:
    """Recursively convert numpy/pandas values into strict JSON values."""
    if isinstance(value, dict):
        return {str(key): sanitize_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize_json(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if not math.isfinite(float(value)) else float(value)
    if value is pd.NA or (isinstance(value, float) and not math.isfinite(value)):
        return None
    return value


def minify_geojson(source: Path, destination: Path, assignment_key: str) -> None:
    payload = json.loads(source.read_text(encoding="utf-8"))
    # Keep only fields required by Plotly and the dashboard.
    for feature in payload.get("features", []):
        properties = feature.get("properties") or {}
        feature["properties"] = {
            "id": str(properties.get("id", "")),
            "name": str(properties.get("name", properties.get("display_name", ""))),
        }
    expression = f'window.DISASTER_DASHBOARD_DATA.geojson["{assignment_key}"]='
    write_js_assignment(destination, expression, payload)


def build(args: argparse.Namespace) -> None:
    processed = args.processed_dir.resolve()
    site = args.site_dir.resolve()
    data_dir = site / "data"
    rows_dir = data_dir / "rows"
    geography_dir = data_dir / "geography"
    for directory in (rows_dir, geography_dir):
        directory.mkdir(parents=True, exist_ok=True)

    finance_path = processed / "finance_processed.csv.gz"
    metadata_path = processed / "metadata.json"
    required = [finance_path, metadata_path]
    for spec in GEO_SPECS.values():
        if spec.get("source_geojson"):
            required.append(processed / spec["source_geojson"])
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required processed files:\n" + "\n".join(missing))

    string_columns = {
        "Year": "string",
        "state_fips": "string",
        "county_geoid": "string",
        "city_id": "string",
        "ua_geoid": "string",
    }
    frame = pd.read_csv(finance_path, dtype=string_columns, low_memory=False)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    # Publish only financial/geographic metadata, never unrelated input metadata.
    allowed_metadata_keys = ['generated_at_utc', 'source_finance_rows', 'dashboard_finance_rows', 'excluded_summary_rows_without_quarter', 'source_city_place_rows', 'state_mapping_coverage_pct', 'county_direct_row_coverage_pct', 'county_city_derived_row_coverage_pct', 'county_enhanced_row_coverage_pct', 'city_matched_row_coverage_pct', 'urban_area_row_coverage_pct', 'county_direct_activity_coverage_pct', 'county_city_derived_activity_coverage_pct', 'county_enhanced_activity_coverage_pct', 'city_matched_activity_coverage_pct', 'urban_area_activity_coverage_pct', 'city_high_confidence_activity_matches', 'city_medium_confidence_activity_matches', 'county_direct_activity_matches', 'county_city_derived_activity_matches', 'unique_grants', 'unique_grantees', 'unique_projects', 'unique_activities', 'quarter_min', 'quarter_max', 'metric_columns', 'city_match_method_counts', 'county_match_method_counts', 'urban_area_match_method_counts', 'geography_note', 'city_data_attribution', 'input_sha256', 'deployment_runtime', 'static_finance_storage', 'static_server_side_authentication']
    metadata = {key: value for key, value in metadata.items() if key in allowed_metadata_keys}
    if "input_sha256" in metadata:
        allowed_sources = {"financial", "state_zip", "county_zip", "urban_area_zip", "cities_csv"}
        metadata["input_sha256"] = {key: value for key, value in metadata["input_sha256"].items() if key in allowed_sources}
    metadata.update({
        "deployment_runtime": "Static HTML/CSS/JavaScript for GitHub Pages; no server process",
        "static_finance_storage": "Dictionary-encoded JavaScript row chunks loaded in the visitor browser",
        "static_server_side_authentication": False,
        "dashboard_edition": "Financial and geographic dashboard v7",
    })

    filter_dictionaries: dict[str, list[str]] = {}
    filter_codes: list[np.ndarray] = []
    for column, key in FILTER_COLUMNS:
        values = sorted_unique(frame[column], year=(column == "Year"))
        filter_dictionaries[key] = values
        filter_codes.append(encode_values(frame[column], values))

    quarter_rows = (
        frame[["quarter_order", "QPR Actual Quarter"]]
        .drop_duplicates()
        .sort_values("quarter_order")
    )
    quarters = quarter_rows["QPR Actual Quarter"].astype(str).tolist()
    quarter_lookup = {label: index for index, label in enumerate(quarters)}
    quarter_codes = np.array([quarter_lookup[str(value)] for value in frame["QPR Actual Quarter"].tolist()], dtype=np.int32)

    grant_codes = factor_codes(frame["Grant"])
    activity_key = frame["Grant"].astype("string").fillna("") + "\x1f" + frame["Activity Number"].astype("string").fillna("")
    activity_codes = factor_codes(activity_key)


    geography: dict[str, Any] = {}
    geography_codes: dict[str, np.ndarray] = {}
    for key, spec in GEO_SPECS.items():
        geography[key], geography_codes[key] = aligned_geography(frame, spec)

    method_specs = [
        ("county_match_method", "countyMethods"),
        ("county_match_confidence", "countyConfidence"),
        ("city_match_method", "cityMethods"),
        ("city_match_confidence", "cityConfidence"),
        ("ua_match_method", "urbanMethods"),
        ("ua_match_confidence", "urbanConfidence"),
    ]
    method_dictionaries: dict[str, list[str]] = {}
    method_codes: list[np.ndarray] = []
    for column, key in method_specs:
        values = sorted_unique(frame[column])
        method_dictionaries[key] = values
        method_codes.append(encode_values(frame[column], values))

    metric_arrays = [
        pd.to_numeric(frame[column], errors="coerce").fillna(0.0).round(2).to_numpy(dtype=float)
        for column in METRIC_COLUMNS
    ]

    row_chunks: list[str] = []
    row_count = len(frame)
    rows_per_chunk = max(1000, int(args.rows_per_chunk))
    for chunk_index, start in enumerate(range(0, row_count, rows_per_chunk)):
        stop = min(row_count, start + rows_per_chunk)
        rows: list[list[Any]] = []
        for index in range(start, stop):
            row = [
                int(filter_codes[0][index]),
                int(filter_codes[1][index]),
                int(filter_codes[2][index]),
                int(filter_codes[3][index]),
                int(filter_codes[4][index]),
                int(filter_codes[5][index]),
                int(filter_codes[6][index]),
                int(quarter_codes[index]),
                int(grant_codes[index]),
                int(activity_codes[index]),
                int(geography_codes["state"][index]),
                int(geography_codes["county"][index]),
                int(geography_codes["city"][index]),
                int(geography_codes["urban"][index]),
                int(method_codes[0][index]),
                int(method_codes[1][index]),
                int(method_codes[2][index]),
                int(method_codes[3][index]),
                int(method_codes[4][index]),
                int(method_codes[5][index]),
                *[float(array[index]) for array in metric_arrays],
            ]
            rows.append(row)
        filename = f"rows_{chunk_index:03d}.js"
        relative = f"data/rows/{filename}"
        write_js_assignment(
            rows_dir / filename,
            "window.DISASTER_DASHBOARD_DATA.rowChunks.push(",
            rows,
        )
        # Close the function-like push expression written above.
        path = rows_dir / filename
        text = path.read_text(encoding="utf-8")
        if text.endswith(";\n"):
            text = text[:-2] + ");\n"
            path.write_text(text, encoding="utf-8")
        row_chunks.append(relative)

    geo_files: dict[str, str] = {}
    for key, spec in GEO_SPECS.items():
        if not spec.get("source_geojson"):
            continue
        destination = geography_dir / f"{key}.js"
        minify_geojson(processed / spec["source_geojson"], destination, key)
        geo_files[key] = f"data/geography/{key}.js"

    bootstrap = {
        "schemaVersion": 2,
        "rowWidth": 25,
        "generatedFor": "GitHub Pages static dashboard",
        "metadata": metadata,
        "columns": COLUMN_INDEX,
        "filters": [
            {"column": column, "key": key, "label": "Project" if column == "Project Title" else column}
            for column, key in FILTER_COLUMNS
        ],
        "filterDictionaries": filter_dictionaries,
        "quarters": quarters,
        "metrics": [
            {"index": index, "label": label, "shortLabel": label.replace("QPR ", "").replace(" $", "")}
            for index, label in enumerate(METRIC_COLUMNS)
        ],
        "geography": geography,
        "geographyLevels": [
            {
                "key": "state",
                "label": "State (direct assignment)",
                "displayLabel": "State",
                "column": COLUMN_INDEX["state"],
                "mapType": "polygon",
                "inferred": False,
                "methodColumn": None,
                "confidenceColumn": None,
            },
            {
                "key": "county",
                "label": "County / county-equivalent (enhanced match)",
                "displayLabel": "County / county-equivalent",
                "column": COLUMN_INDEX["county"],
                "mapType": "polygon",
                "inferred": True,
                "methodColumn": COLUMN_INDEX["countyMethod"],
                "confidenceColumn": COLUMN_INDEX["countyConfidence"],
                "methodDictionary": "countyMethods",
                "confidenceDictionary": "countyConfidence",
            },
            {
                "key": "city",
                "label": "City / populated place (matched point)",
                "displayLabel": "City / populated place",
                "column": COLUMN_INDEX["city"],
                "mapType": "point",
                "inferred": True,
                "methodColumn": COLUMN_INDEX["cityMethod"],
                "confidenceColumn": COLUMN_INDEX["cityConfidence"],
                "methodDictionary": "cityMethods",
                "confidenceDictionary": "cityConfidence",
            },
            {
                "key": "urban",
                "label": "2010 Census urban area (secondary match)",
                "displayLabel": "2010 Census urban area",
                "column": COLUMN_INDEX["urban"],
                "mapType": "polygon",
                "inferred": True,
                "methodColumn": COLUMN_INDEX["urbanMethod"],
                "confidenceColumn": COLUMN_INDEX["urbanConfidence"],
                "methodDictionary": "urbanMethods",
                "confidenceDictionary": "urbanConfidence",
            },
        ],
        "methodDictionaries": method_dictionaries,
        "rowChunkFiles": row_chunks,
        "geoFiles": geo_files,
        "rowChunks": [],
        "geojson": {},
    }
    bootstrap = sanitize_json(bootstrap)
    write_js_assignment(
        data_dir / "bootstrap.js",
        "window.DISASTER_DASHBOARD_DATA=",
        bootstrap,
    )

    # Human-readable metadata copy for QA and citation.
    (data_dir / "metadata.json").write_text(
        json.dumps(sanitize_json(metadata), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (data_dir / "STATIC_DATA_SCHEMA.md").write_text(
        "# Static data schema\n\n"
        "The dashboard stores finance records as compact arrays in `data/rows/*.js`. "
        "Column positions are declared in `data/bootstrap.js` under `columns`. "
        "Repeated text is dictionary-encoded and geographic boundaries are loaded lazily.\n\n"
        "The deployment package contains no Python runtime, SQLite database, or raw source CSV.\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "finance_rows": row_count,
        "row_chunks": len(row_chunks),
        "site_dir": str(site),
    }, indent=2))


if __name__ == "__main__":
    build(parse_args())
