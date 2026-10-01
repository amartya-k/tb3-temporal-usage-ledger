"""Host-only verifier sensitivity check against deliberately incorrect references.

Uses trusted reference variants, never submitted agent code. Docker oracle/nop
remain the authoritative end-to-end verification; this host has no Docker.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1] / 'tasks/temporal-usage-ledger'
MUTATIONS = {
    'bill_buffered_events': ('if seq > frontier.get(source, 0):', 'if False:'),
    'lose_original_receipt': ('response = json.loads(prior[1])', 'response = dispatch(c, req)'),
    'ignore_invoice_cas': ('if version != req["expected_version"]:', 'if False:'),
    'forget_previous_invoice': ('row[key] = current.get(name, {}).get(key, 0) - previous.get(name, {}).get(key, 0)',
                            'row[key] = current.get(name, {}).get(key, 0)'),
    'acknowledge_prefix': ('UPDATE documents SET acked=1 WHERE seq=?', 'UPDATE documents SET acked=1 WHERE seq<=?'),
    'commit_partial_ingest': ('logical[key] = raw\n        c.execute(', 'logical[key] = raw\n        c.commit()\n        c.execute('),
    'ignore_causal_predecessors': ('all(marks.get(k, 0) >= n for k, n in required.items())', 'True'),
    'accept_open_frontier': ('if seq <= cuts.get(source, 0) and any(n > cuts.get(k, 0) for k, n in json.loads(raw).items()):', 'if False:'),
    'forget_dependency_on_replay': ('(json.loads(old[0]) if old else {}) != required', 'False'),
}


def run():
    with tempfile.TemporaryDirectory(prefix='ledger-mutants-') as tmp:
        base = Path(tmp)
        tests = base / 'tests'
        shutil.copytree(ROOT / 'tests', tests)
        program = base / 'app'
        shutil.copytree(ROOT / 'solution', program)
        for path in tests.glob('*.py'):
            text = path.read_text().replace('/usr/local/bin/python', sys.executable).replace('/app/app/', str(program) + '/')
            if path.name == 'test_billing.py':
                start = text.index('    libc = ctypes.CDLL')
                end = text.index('\n\ndef independent', start)
                text = text[:start] + '    pass  # trusted host-only reference variants\n' + text[end:]
            path.write_text(text)
        source = (program / 'ledger.py').read_text()
        missed = []
        for name, (old, new) in MUTATIONS.items():
            assert source.count(old) == 1, name
            (program / 'ledger.py').write_text(source.replace(old, new))
            result = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-x', '--tb=no', str(tests / 'test_ledger.py')], capture_output=True, text=True)
            caught = result.returncode == 1 and 'failed' in result.stdout
            print(name, 'DETECTED' if caught else 'NOT DETECTED', flush=True)
            if not caught:
                missed.append(name)
                print(result.stdout[-1000:], result.stderr[-1000:])
        if missed:
            raise SystemExit(f'Undetected variants: {missed}')


if __name__ == '__main__':
    run()
