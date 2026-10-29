#!/usr/bin/env python3
"""Validate the English edition against a trusted pre-edit checkout (Python >= 3.12).

Usage: python scripts/validate_portfolio.py --original-root /path/to/base-checkout --archive-only
The original checkout must be commit a3bc52f16e600f914ce0c0165173fd267ab02620.
This script performs static checks only; it never executes archived source.
"""
import argparse
import ast
import base64
import csv
import gzip
import hashlib
import io
import json
import re
import tarfile
import tokenize
import urllib.parse
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CJK = re.compile(r'[\u3400-\u9fff]')
IGNORED = {tokenize.COMMENT, tokenize.NL, tokenize.ENCODING, tokenize.ENDMARKER}
# These patterns flag candidates, not proof that an arbitrary string is a secret.
PATTERNS = {
    'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'github_token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})\b'),
    'aws_access_id': re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'service_token': re.compile(r'\b(?:sk-[A-Za-z0-9_-]{24,}|hf_[A-Za-z0-9]{25,}|KGAT_[A-Za-z0-9_-]{20,})\b'),
    'literal_credential': re.compile(r'''(?i)(?:api[_-]?key|access[_-]?token|auth[_-]?token|password)["']?\s*[:=]\s*["']([A-Za-z0-9_+/=.-]{20,})["']'''),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token_list(source):
    return list(tokenize.generate_tokens(io.StringIO(source).readline))


def source(cell):
    return ''.join(cell['source'])


def markdown_links(text):
    # This repository uses inline links (no nested parentheses in local targets).
    return re.findall(r'!?\[[^\]\n]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)', text)


def heading_anchors(text):
    counts = Counter()
    anchors = set()
    for title in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', text, re.M):
        title = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', title)
        slug = re.sub(r'[^\w\-\s]', '', title.lower()).replace(' ', '-')
        n = counts[slug]
        counts[slug] += 1
        anchors.add(slug + (f'-{n}' if n else ''))
    return anchors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-root', type=Path, required=True)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--archive-only', action='store_true',
                        help='Restrict project checks to the nine notebook archives in meta/catalog.json')
    args = parser.parse_args()
    original = args.original_root
    report = {'baseline_commit': 'a3bc52f16e600f914ce0c0165173fd267ab02620',
              'scope': 'nine_notebook_archives_and_supporting_docs' if args.archive_only else 'repository',
              'errors': [], 'files': [], 'local_links_checked': 0,
              'credential_flags': [], 'decoded_embedded_items_scanned': 0}
    errors = report['errors']
    ledger = json.loads((ROOT/'meta/translation-exceptions.json').read_text())['literal_changes']
    used = Counter()
    catalog = json.loads((ROOT/'meta/catalog.json').read_text())['projects']
    retained_projects = {item['project'] for item in catalog}
    for p in sorted((original/'projects').rglob('*')):
        if p.suffix not in ('.py', '.ipynb') or p.relative_to(original).parts[1] not in retained_projects:
            continue
        rel = str(p.relative_to(original))
        current = ROOT/rel
        old = p.read_text()
        new = current.read_text()
        if p.suffix == '.py':
            ast.parse(new)
            if p.read_bytes() != current.read_bytes():
                errors.append(f'Archived Python changed: {rel}')
            report['files'].append({'path': rel, 'byte_identical': p.read_bytes() == current.read_bytes()})
            continue
        a, b = json.loads(old), json.loads(new)
        if len(a['cells']) != len(b['cells']):
            errors.append(f'Cell count changed: {rel}')
            continue
        strict = normalized = code = translated_markdown = exact_unlexable = 0
        for i, (ac, bc) in enumerate(zip(a['cells'], b['cells'])):
            sa, sb = source(ac), source(bc)
            if {k: v for k, v in ac.items() if k != 'source'} != {k: v for k, v in bc.items() if k != 'source'}:
                errors.append(f'Non-source cell content changed: {rel}:{i}')
            if ac['cell_type'] == 'markdown':
                translated_markdown += sa != sb
                if CJK.search(sb):
                    errors.append(f'Chinese Markdown remains: {rel}:{i}')
                if not CJK.search(sa) and sa != sb:
                    errors.append(f'Original English Markdown changed: {rel}:{i}')
                continue
            code += 1
            try:
                ta, tb = token_list(sa), token_list(sb)
            except (tokenize.TokenError, IndentationError, SyntaxError):
                # Historical shell/R cells are not necessarily Python-lexable.
                if sa != sb:
                    errors.append(f'Changed non-Python-lexable cell: {rel}:{i}')
                else:
                    exact_unlexable += 1
                continue
            # Check unchanged English comments, including author credits.
            ca = [t.string for t in ta if t.type == tokenize.COMMENT and not CJK.search(t.string)]
            cb = [t.string for t in tb if t.type == tokenize.COMMENT]
            pos = 0
            for comment in ca:
                try:
                    pos = cb.index(comment, pos) + 1
                except ValueError:
                    errors.append(f'Original English comment changed: {rel}:{i}')
                    break
            if any(CJK.search(t.string) for t in tb if t.type == tokenize.COMMENT):
                errors.append(f'Chinese comment remains: {rel}:{i}')
            aa = [(t.type, t.string) for t in ta if t.type not in IGNORED]
            bb = [(t.type, t.string) for t in tb if t.type not in IGNORED]
            strict += aa == bb
            expected = []
            for t in ta:
                if t.type in IGNORED:
                    continue
                matches = [(j, x) for j, x in enumerate(ledger)
                           if x['path'] == rel and x['cell_index'] == i
                           and x['line'] == t.start[0] and x['before'] == t.string]
                value = t.string
                if matches:
                    if len(matches) != 1:
                        errors.append(f'Ambiguous literal exception: {rel}:{i}:{t.start[0]}')
                    j, x = matches[0]
                    value = x['after']
                    used[j] += 1
                expected.append((t.type, value))
            normalized += expected == bb
            if expected != bb:
                errors.append(f'Non-whitelisted token change: {rel}:{i}')
        if {k: v for k, v in a.items() if k != 'cells'} != {k: v for k, v in b.items() if k != 'cells'}:
            errors.append(f'Notebook metadata changed: {rel}')
        report['files'].append({'path': rel, 'code_cells': code,
                                'strict_noncomment_token_equality_cells': strict,
                                'token_equality_with_exact_literal_exceptions_cells': normalized,
                                'translated_markdown_cells': translated_markdown,
                                'non_python_lexable_cells_source_identical': exact_unlexable})
    if set(used) != set(range(len(ledger))) or any(n != 1 for n in used.values()):
        errors.append('Literal ledger does not match actual changes exactly once per occurrence')
    report['verified_literal_exceptions'] = sum(used.values())
    old_catalog = {p['project']: p for p in json.loads((original/'catalog.json').read_text())['projects']}
    for p in catalog:
        if digest(ROOT/p['archived_file']) != p['translated_sha256'] or p['archived_sha256'] != p['translated_sha256']:
            errors.append(f'Current hash mismatch: {p["project"]}')
        o = old_catalog[p['project']]
        if p['original']['download_sha256'] != o['original_download_sha256'] or p['original']['archived_sha256'] != o['archived_sha256']:
            errors.append(f'Original provenance changed: {p["project"]}')
        if digest(original/p['archived_file']) != p['original']['archived_sha256']:
            errors.append(f'Baseline hash mismatch: {p["project"]}')
        if json.loads((ROOT/p['provenance_file']).read_text()) != p:
            errors.append(f'Catalog/provenance mismatch: {p["project"]}')
    for item in json.loads((ROOT/'meta/output-provenance.json').read_text())['outputs']:
        if 'sha256' in item and digest(ROOT/item['path']) != item['sha256']:
            errors.append(f'Figure hash mismatch: {item["path"]}')

    def scan(label, data, depth=0):
        text = data.decode('utf-8', 'replace')
        for name, pattern in PATTERNS.items():
            if pattern.search(text):
                report['credential_flags'].append({'path': label, 'pattern': name})
        if depth >= 2:
            return
        # Inspect existing opaque literal blobs without writing or executing them.
        for value in re.findall(r'[A-Za-z0-9+/]{200,}={0,2}', text):
            try:
                decoded = base64.b64decode(value, validate=True)
                if decoded[:2] != b'\x1f\x8b':
                    continue
                with gzip.GzipFile(fileobj=io.BytesIO(decoded)) as stream:
                    expanded = stream.read(20_000_001)
                if len(expanded) > 20_000_000:
                    errors.append(f'Embedded blob exceeds scan limit: {label}')
                    continue
                report['decoded_embedded_items_scanned'] += 1
                scan(label + ':decoded-gzip', expanded, depth+1)
                try:
                    with tarfile.open(fileobj=io.BytesIO(expanded), mode='r:') as archive:
                        for member in archive.getmembers():
                            if member.isfile() and member.size < 20_000_000:
                                scan(label + ':embedded/' + member.name, archive.extractfile(member).read(), depth+1)
                except tarfile.ReadError:
                    pass
            except (ValueError, OSError, EOFError):
                continue

    public_manifest_schemas = {
        'projects/11-knee-report-label-accuracy/analysis/datasets.csv': 'dataset,filename,cohort_role,ancestry,half_is_unknown,version,license,metadata_url,source_url,checked_date,schema_rows,schema_columns,schema_checked,download_allowed'.split(','),
        'projects/11-knee-report-label-accuracy/analysis/discovery.csv': 'ref,licenseName,currentVersionNumber,screening_status'.split(','),
        'projects/11-knee-report-label-accuracy/analysis/parameters.csv': 'parameter,value,unit,source_url,source_location,source_date,accessed_date,status,use'.split(','),
    }
    # Exact aggregate result schemas; individual-level files are not accepted.
    public_manifest_schemas.update({
        'projects/11-knee-report-label-accuracy/results/T4_agreement.csv': ['finding', 'metric', 'source_a', 'source_b', 'estimate', 'lower', 'upper', 'bootstrap_valid', 'bootstrap_attempted'],
        'projects/11-knee-report-label-accuracy/results/T4_denominators.csv': ['finding', 'source', 'cohort_n', 'known_n', 'positive_n', 'complete_case_n', 'majority_comparable_n', 'majority_disagreements'],
        'projects/11-knee-report-label-accuracy/results/T4_pair_denominators.csv': ['finding', 'source_a', 'source_b', 'pair_known_n', 'disagreement_pair_n'],
        'projects/11-knee-report-label-accuracy/results/T4_sensitivity.csv': ['variant', 'finding', 'statistic', 'estimate'],
        'projects/11-knee-report-label-accuracy/results/T6_eligibility.csv': ['finding', 'complete_case_n', 'eligible', 'reason'],
        'projects/11-knee-report-label-accuracy/results/T6_latent_parameters.csv': ['parameter', 'median', 'lower', 'upper', 'rhat', 'ess_bulk', 'ess_tail', 'boundary_fraction', 'finding', 'prior', 'complete_case_n', 'extended', 'source', 'diagnostics_pass'],
        'projects/11-knee-report-label-accuracy/results/T6_pattern_checks.csv': ['finding', 'pattern', 'observed_count', 'expected_proportion', 'predictive_lower', 'predictive_upper'],
        'projects/11-knee-report-label-accuracy/results/T6_predictive_checks.csv': ['finding', 'complete_case_n', 'discrepancy', 'posterior_predictive_p', 'draws', 'observed_discrepancy_median', 'replicated_discrepancy_median'],
        'projects/11-knee-report-label-accuracy/results/T7_dgm.csv': ['n', 'rho', 'replicates', 'realized_prevalence', 'realized_sensitivity', 'realized_specificity', 'correction_factor', 'max_bias_mcse', 'target_mcse_met'],
        'projects/11-knee-report-label-accuracy/results/T7_ordering.csv': ['n', 'rho', 'method', 'attempted', 'valid', 'correct_order', 'correct_order_mcse', 'tie_rate', 'reversed_order', 'superiority_rate', 'intervals_valid', 'tie_mcse', 'reversal_mcse', 'superiority_mcse'],
        'projects/11-knee-report-label-accuracy/results/T7_simulation.csv': ['n', 'rho', 'method', 'estimand', 'replicates_attempted', 'estimates_valid', 'intervals_valid', 'truth', 'mean_estimate', 'bias', 'bias_mcse', 'empirical_sd', 'sd_mcse', 'rmse', 'rmse_mcse', 'coverage', 'coverage_mcse', 'mean_interval_width', 'width_mcse', 'failure_rate', 'failure_mcse', 'interval_failure_rate', 'interval_failure_mcse', 'out_of_range', 'out_of_range_mcse'],
        'projects/11-knee-report-label-accuracy/results/T5_clusters.csv': ['variant', 'source_a', 'source_b', 'mean_or_median_kappa', 'same_cluster_k2', 'bootstrap_same_cluster', 'bootstrap_replicates'],
        'projects/11-knee-report-label-accuracy/results/T5_membership.csv': ['variant', 'source', 'cluster_k2'],
        'projects/11-knee-report-label-accuracy/results/T5_focus.csv': ['finding', 'source_a', 'source_b', 'kappa', 'lower', 'upper', 'pair_known_n'],
        'projects/11-knee-report-label-accuracy/results/T8_interval_sensitivity.csv': ['method', 'n', 'prevalence', 'true_auc', 'replicates', 'intervals_valid', 'coverage', 'coverage_mcse', 'successful_coverage', 'successful_coverage_mcse', 'interval_failure_rate', 'failure_mcse', 'mean_width', 'width_mcse', 'paired_success_difference', 'paired_difference_mcse'],
        'projects/11-knee-report-label-accuracy/results/T8_sample_diagnostics.csv': ['replicates', 'n', 'mean_positives', 'positive_q025', 'positive_median', 'positive_q975', 'fewer_than_two_positives', 'boundary_auc', 'zero_delong_variance', 'mean_auc', 'bias', 'bias_mcse'],
        'projects/11-knee-report-label-accuracy/results/source_files.csv': ['dataset', 'filename', 'version', 'license', 'source_url', 'sha256', 'bytes'],
    })
    forbidden = {'.pth', '.pt', '.ckpt', '.safetensors', '.parquet', '.dcm', '.npy', '.npz', '.zip', '.tar', '.gz', '.rds', '.RData', '.duckdb', '.wal', '.part'}
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts:
            continue
        rel = str(p.relative_to(ROOT))
        parts = p.relative_to(ROOT).parts
        if args.archive_only and parts[0] == 'projects' and len(parts) > 1 and parts[1] not in retained_projects:
            continue
        if p.suffix in forbidden or p.name in {'kaggle.json', '.env', 'access_token'}:
            errors.append(f'Data/model/credential file in package: {rel}')
        if p.suffix == '.csv' and rel != 'meta/catalog.csv':
            if rel not in public_manifest_schemas:
                errors.append(f'Unexpected CSV: {rel}')
            else:
                with p.open(newline='') as stream:
                    rows = list(csv.reader(stream))
                if not rows or rows[0] != public_manifest_schemas[rel] or any(len(r) != len(rows[0]) for r in rows):
                    errors.append(f'Invalid public source-manifest schema: {rel}')
        if p.suffix in ('.md', '.json', '.py', '.ipynb', '.csv', '.txt', '.R', '.qmd', '.lock'):
            text = p.read_text()
            if rel != 'meta/validation.json':
                scan(rel, p.read_bytes())
            if p.suffix in ('.json', '.ipynb'):
                json.loads(text)
            if p.suffix == '.py':
                ast.parse(text)
            md_parts = [text] if p.suffix in ('.md', '.qmd') else [source(c) for c in json.loads(text)['cells'] if c['cell_type'] == 'markdown'] if p.suffix == '.ipynb' else []
            for md in md_parts:
                if CJK.search(md):
                    errors.append(f'Chinese reader-facing Markdown: {rel}')
                for url in markdown_links(md):
                    parsed = urllib.parse.urlsplit(url.strip('<>'))
                    if parsed.scheme or parsed.netloc:
                        continue
                    report['local_links_checked'] += 1
                    target = (p.parent / urllib.parse.unquote(parsed.path)).resolve() if parsed.path else p
                    if not target.exists():
                        errors.append(f'Broken local link in {rel}: {url}')
                    elif parsed.fragment:
                        dest = target/'README.md' if target.is_dir() else target
                        if dest.suffix == '.md' and parsed.fragment not in heading_anchors(dest.read_text()):
                            errors.append(f'Broken local anchor in {rel}: {url}')
    report['notebooks'] = sum('code_cells' in x for x in report['files'])
    report['archived_python_files'] = sum('byte_identical' in x for x in report['files'])
    report['code_cells'] = sum(x.get('code_cells', 0) for x in report['files'])
    report['strict_noncomment_token_equality_cells'] = sum(x.get('strict_noncomment_token_equality_cells', 0) for x in report['files'])
    report['token_equality_with_exact_literal_exceptions_cells'] = sum(x.get('token_equality_with_exact_literal_exceptions_cells', 0) for x in report['files'])
    report['non_python_lexable_cells_source_identical'] = sum(x.get('non_python_lexable_cells_source_identical', 0) for x in report['files'])
    report['translated_markdown_cells'] = sum(x.get('translated_markdown_cells', 0) for x in report['files'])
    report['passed'] = not errors and not report['credential_flags']
    if args.report:
        args.report.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'files'}, indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
