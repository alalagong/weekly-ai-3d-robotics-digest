"""Audit report overlap without reading or searching papers again."""
import collections
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREFIXES = ['2026-10-03_2026-10-18', '2026-10-18_2026-10-24', '2026-10-24_2026-11-01']

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def version(row):
    return str(row.get('version', '')).lstrip('v')

def included(row):
    return row['disposition'] in ('deep_read', 'supplemental', 'revision_tracking')

def fingerprint(row):
    return ' '.join(row.get('abstract', '').split())

def main():
    ledgers = [load(ROOT / 'reports' / (prefix + '_paper-ledger.json')) for prefix in PREFIXES]
    result = {'method': 'Compare base IDs and exact versions; abstract_read is a stored evidence flag, not a token bill or proof of a separate model call.', 'periods': [], 'pairs': []}
    previous_included = {}
    previous_all = {}
    for prefix, ledger in zip(PREFIXES, ledgers):
        rows = ledger['papers']
        inc = [r for r in rows if included(r)]
        overlap = [r for r in inc if r['id'] in previous_included]
        same = [r for r in overlap if version(r) == version(previous_included[r['id']])]
        candidates = [r for r in rows if r['id'] in previous_all and version(r) == version(previous_all[r['id']])]
        read_again = [r for r in candidates if r.get('abstract_read') and previous_all[r['id']].get('abstract_read')]
        result['periods'].append({'prefix': prefix, 'candidate_count': len(rows), 'included_count': len(inc), 'prior_included_ids': len(overlap), 'same_version_reincluded_count': len(same), 'same_version_reincluded_ids': [r['id'] for r in same], 'prior_same_version_candidates': len(candidates), 'both_periods_abstract_read_flags': len(read_again), 'both_periods_read_previously_included': sum(included(previous_all[r['id']]) for r in read_again), 'both_read_ids': [r['id'] for r in read_again], 'prior_excluded_now_included_same_version': [r['id'] for r in candidates if included(r) and not included(previous_all[r['id']])], 'version_updates': [{'id': r['id'], 'title': r['title'], 'previous_version': version(previous_included[r['id']]), 'current_version': version(r), 'window_class': r.get('window_class'), 'normalized_abstract_unchanged': bool(fingerprint(r)) and fingerprint(r) == fingerprint(previous_included[r['id']])} for r in overlap]})
        previous_included.update({r['id']: r for r in inc})
        previous_all.update({r['id']: r for r in rows})
    for (a, la), (b, lb) in itertools.combinations(zip(PREFIXES, ledgers), 2):
        ar = {r['id']: r for r in la['papers'] if included(r)}
        br = {r['id']: r for r in lb['papers'] if included(r)}
        ids = sorted(ar.keys() & br.keys())
        result['pairs'].append({'first': a, 'second': b, 'shared_included_ids': len(ids), 'same_version': [i for i in ids if version(ar[i]) == version(br[i])], 'deep_read_in_both': [i for i in ids if ar[i]['disposition'] == br[i]['disposition'] == 'deep_read']})
    work = ROOT / 'reports' / (PREFIXES[-1] + '_work')
    sources = ['core-search.json', 'geometry-search.json', 'extension-screened.json']
    read_sets = {}
    for name in sources:
        data = load(work / name)
        rows = data.get('papers', data.get('candidates', []))
        read_sets[name] = {r['id'] for r in rows if r.get('abstract_read')}
    union = set().union(*read_sets.values())
    result['within_run_abstract_flags'] = {'per_task': {n: len(s) for n, s in read_sets.items()}, 'total_marks': sum(map(len, read_sets.values())), 'unique_ids': len(union), 'excess_marks_over_unique_ids': sum(map(len, read_sets.values())) - len(union), 'pairwise': [{'a': a, 'b': b, 'overlap': len(read_sets[a] & read_sets[b])} for a, b in itertools.combinations(sources, 2)]}
    result['queries'] = []
    for name in ['main-search-manifest.json', 'main-advanced-manifest.json', 'review-query-manifest.json']:
        rows = load(work / name)
        result['queries'].append({'source': name, 'queries': len(rows), 'fetched_hits': sum(r.get('fetched', r.get('returned', 0)) for r in rows), 'large_queries': [{'family': r.get('family'), 'name': r.get('name'), 'total': r.get('total')} for r in rows if r.get('total', 0) > 200]})
    out = ROOT / 'reports' / '2026-11-07_三期论文重复与流程审计.json'
    out.write_bytes(json.dumps(result, ensure_ascii=False, indent=2).encode('utf8'))
    print(json.dumps({'periods': [{k: v for k, v in r.items() if k not in ('both_read_ids', 'version_updates')} for r in result['periods']], 'pairs': result['pairs'], 'within_run': result['within_run_abstract_flags']}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
