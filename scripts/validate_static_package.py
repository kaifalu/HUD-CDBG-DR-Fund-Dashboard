#!/usr/bin/env python3
"""Validate the financial/geographic site, embedded HTML, and package hashes.

Usage: python scripts/validate_static_package.py [--site-dir PATH] [--json-out PATH]
Only Python's standard library is required. This checker does not alter data.
"""
from __future__ import annotations
import argparse,base64,gzip,hashlib,json,math,re,sys
from html.parser import HTMLParser
from pathlib import Path

EXPECTED_COLUMNS = {name:i for i,name in enumerate([
    'year','disasterType','grantee','project','organization','activityType','activityTitle',
    'quarter','grantCode','activityCode','state','county','city','urban','countyMethod',
    'countyConfidence','cityMethod','cityConfidence','urbanMethod','urbanConfidence','metricStart'])}

class EmbeddedParser(HTMLParser):
    def __init__(self):
        super().__init__();self.assets={};self.current=None;self.external=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script' and a.get('type')=='application/x-cdbg-gzip':
            self.current=a['data-cdbg-path'];self.assets[self.current]=''
        if tag=='script' and a.get('src'):self.external.append(a['src'])
        if tag=='link' and a.get('rel')=='stylesheet':self.external.append(a.get('href',''))
    def handle_data(self,data):
        if self.current:self.assets[self.current]+=data
    def handle_endtag(self,tag):
        if tag=='script':self.current=None

def assignment(path,prefix,suffix=';'):
    text=path.read_text(encoding='utf-8').strip()
    if not text.startswith(prefix) or not text.endswith(suffix):raise ValueError(f'Unexpected data assignment: {path.name}')
    return json.loads(text[len(prefix):-len(suffix)])

def validate(root:Path)->dict:
    root=root.resolve();failures=[];checks={}
    def check(name,condition):
        checks[name]=bool(condition)
        if not condition:failures.append(name)
    for rel in ['index.html','.nojekyll','assets/app.js','assets/app.css','assets/vendor/plotly-3.3.1.min.js','data/bootstrap.js','data/metadata.json','HUD-CDBG-DR-Fund-Dashboard-Hierarchical.html']:
        check('present:'+rel,(root/rel).is_file())
    if failures:raise ValueError('; '.join(failures))
    dd=assignment(root/'data/bootstrap.js','window.DISASTER_DASHBOARD_DATA=')
    check('schema_columns',dd['columns']==EXPECTED_COLUMNS)
    check('schema_version_and_width',dd.get('schemaVersion')==2 and dd.get('rowWidth')==25)
    check('seven_filters',len(dd['filters'])==7)
    check('five_metrics',len(dd['metrics'])==5)
    check('four_geographies',set(dd['geography'])=={'state','county','city','urban'})
    check('metadata_copies_match',dd['metadata']==json.loads((root/'data/metadata.json').read_text()))
    forbidden=re.compile(r'narrativ|privacy|address_mentions',re.I)
    def keycheck(obj):
        if isinstance(obj,dict):return all(not forbidden.search(str(k)) and keycheck(v) for k,v in obj.items())
        if isinstance(obj,list):return all(keycheck(v) for v in obj)
        return True
    check('no_narrative_metadata_or_links',keycheck(dd))
    files=[p for p in root.rglob('*') if p.is_file()]
    check('no_narrative_payload_or_privacy_files',not any(re.search(r'narrativ|sanitize_narratives|(^|/)privacy/',str(p.relative_to(root)),re.I) for p in files))
    for rel in ['index.html','assets/app.js','assets/app.css','scripts/build_static_data.py','scripts/build_self_contained.py']:
        check('clean_code:'+rel,not re.search(r'narrativ|PUBLIC_ADDRESS|pii-redaction',(root/rel).read_text(),re.I))
    count=0;sums=[0]*5;coverage={k:0 for k in dd['geography']};indices_ok=True
    for rel in dd['rowChunkFiles']:
        rows=assignment(root/rel,'window.DISASTER_DASHBOARD_DATA.rowChunks.push(',');')
        for row in rows:
            if len(row)!=25 or any(not isinstance(x,(float,int)) or not math.isfinite(x) for x in row):
                raise ValueError(f'Invalid compact row in {rel}')
            for i,fltr in enumerate(dd['filters']):
                indices_ok &= -1<=row[i]<len(dd['filterDictionaries'][fltr['key']])
            indices_ok &= 0<=row[7]<len(dd['quarters'])
            for level in dd['geographyLevels']:
                k=level['key'];col=level['column']
                indices_ok &= col==EXPECTED_COLUMNS[k] and -1<=row[col]<len(dd['geography'][k]['ids'])
                coverage[k]+=int(row[col]>=0)
            for i in range(5):sums[i]+=round(row[20+i]*100)
        count+=len(rows)
    check('valid_dictionary_and_geography_indices',indices_ok)
    check('financial_row_count',count==dd['metadata']['dashboard_finance_rows'])
    baseline_path=root/'docs/data_preservation_check.json'
    if baseline_path.exists():
        baseline=json.loads(baseline_path.read_text())
        check('financial_totals_preserved',sums==list(baseline['financial_totals_in_cents'].values()))
        check('financial_row_count_preserved',count==baseline['finance_rows'])
    for level,path in dd['geoFiles'].items():
        payload=assignment(root/path,f'window.DISASTER_DASHBOARD_DATA.geojson["{level}"]=')
        check('geojson:'+level,payload.get('type')=='FeatureCollection' and len(payload.get('features',[]))>0)
    parser=EmbeddedParser();parser.feed((root/'HUD-CDBG-DR-Fund-Dashboard-Hierarchical.html').read_text())
    allowed={'assets/app.js','data/bootstrap.js','assets/vendor/plotly-3.3.1.min.js',*dd['rowChunkFiles'],*dd['geoFiles'].values()}
    check('standalone_exact_asset_list',set(parser.assets)==allowed)
    check('standalone_no_external_scripts_or_css',not parser.external)
    for rel,encoded in parser.assets.items():
        decoded=gzip.decompress(base64.b64decode(encoded))
        check('embedded_matches:'+rel,decoded==(root/rel).read_bytes())
    manifest=root/'PACKAGE_CONTENTS_SHA256.txt'
    verified=0
    if manifest.is_file():
        manifest_paths=set()
        for line in manifest.read_text().splitlines():
            if not line.strip():continue
            digest,rel=line.split('  ',1);manifest_paths.add(rel)
            p=root/rel
            check('hash:'+rel,p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
            verified+=1
        actual={str(p.relative_to(root)).replace('\\','/') for p in files if p!=manifest and '__pycache__' not in p.parts}
        check('manifest_complete',manifest_paths==actual)
    return {'passed':not failures,'failures':failures,'finance_rows':count,'row_width':25,'row_chunks':len(dd['rowChunkFiles']),
            'embedded_assets':len(parser.assets),'mapped_rows':coverage,'financial_totals_in_cents':dict(zip((m['label'] for m in dd['metrics']),sums)),
            'verified_package_hashes':verified,'checks':checks}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--site-dir',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--json-out',type=Path)
    args=p.parse_args()
    result=validate(args.site_dir)
    text=json.dumps(result,indent=2)+'\n'
    print(text)
    if args.json_out:args.json_out.write_text(text,encoding='utf-8')
    if not result['passed']:sys.exit(1)
if __name__=='__main__':main()
