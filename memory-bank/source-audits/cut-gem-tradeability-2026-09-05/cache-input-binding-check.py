from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, zipfile
root = Path.cwd()
output = root / 'tmp/review/cut-gem-provenance-supplement.json'


def git(*args, cwd=root):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


base = Path('/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2')
proof = {'captured_at_utc': datetime.now(timezone.utc).isoformat(), 'repository_root': str(root), 'repository_commit': git('rev-parse', 'HEAD'), 'actual_original_query_cwd': str(root), 'original_query_started_at_utc': '2026-09-05T20:32:27.829519Z', 'query_sources': [], 'cache_inputs': [], 'qualification': 'No earlier extracted-input byte comparison is claimed. This supplement compares every archive file with the actual extracted query inputs at supplement capture time. Original query output is unchanged and was not rerun.'}
for rel in ('tools/query_openrs2_cache.sh', 'tools/OpenRs2CacheItemSearch.java'):
    p = root / rel
    proof['query_sources'].append({'path': str(p), 'repository_root': str(root), 'commit': git('rev-parse', 'HEAD'), 'git_blob': git('rev-parse', f'HEAD:{rel}'), 'sha256': sha(p), 'bytes': p.stat().st_size, 'is_symlink': p.is_symlink(), 'tracked': git('ls-files', '--error-unmatch', rel) == rel})
core = Path.home() / '.gradle/caches/modules-2/files-2.1/rs.darkan/core/2.0.5'
proof['darkan_decoder_dependency'] = {'version': '2.0.5', 'root': str(core), 'jars': [{'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted(core.rglob('*.jar'))], 'qualification': 'The AnkiScape Java query source imports Darkan classes from the Gradle dependency; the wrapper and Java source are tracked in AnkiScape.'}
for rev, date, index in ((727, '2012-07-24', 309), (742, '2012-11-07', 544)):
    archive = base / f'runescape-{rev}-{date}-openrs2-{index}-disk.zip'
    parent = base / f'extracted/{rev}-{date}'
    extracted = parent / 'cache'
    members = []
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            p = parent / info.filename
            with z.open(info) as f:
                zh = hashlib.file_digest(f, 'sha256').hexdigest()
            assert p.is_file(), p
            assert p.stat().st_size == info.file_size, p
            eh = sha(p)
            assert zh == eh, (p, zh, eh)
            members.append({'zip_member': info.filename, 'extracted_path': str(p), 'bytes': info.file_size, 'zip_member_sha256': zh, 'extracted_sha256': eh, 'equal': True})
    expected = {str(parent / r['zip_member']) for r in members}
    actual = {str(p) for p in extracted.rglob('*') if p.is_file()}
    assert expected == actual, {'extra': sorted(actual - expected), 'missing': sorted(expected - actual)}
    out = root / f'memory-bank/source-audits/cut-gem-tradeability-2026-09-05/cache-{rev}-items-1611-1613.txt'
    proof['cache_inputs'].append({'revision': rev, 'date': date, 'archive_path': str(archive), 'archive_bytes': archive.stat().st_size, 'archive_sha256': sha(archive), 'query_cwd': str(root), 'query_argv': [str(root / 'tools/query_openrs2_cache.sh'), str(extracted), '--id', '1611', '1613'], 'query_stdout_path': str(out), 'query_stdout_sha256': sha(out), 'members': members, 'member_count': len(members), 'total_uncompressed_bytes': sum((r['bytes'] for r in members)), 'no_extra_or_missing_extracted_files': True})
output.write_text(json.dumps(proof, indent=2) + '\n')
print(json.dumps({'output': str(output), 'bytes': output.stat().st_size, 'sha256': sha(output), 'cache_summaries': [{k: v for k, v in r.items() if k in ('revision', 'member_count', 'total_uncompressed_bytes', 'no_extra_or_missing_extracted_files')} for r in proof['cache_inputs']]}, indent=2))
