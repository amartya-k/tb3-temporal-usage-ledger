"""Minimal synthetic incident: a gap must buffer usage until seq=1 arrives."""
import json
import subprocess
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    event = {'source':'west', 'seq':2, 'kind':'sessions', 'payload':
             {'id':'meter-1','account':'acme','start':0,'end':10,'units':10,
              'recorded':1,'revision':1,'cancelled':False}}
    request = {'op':'ingest','request_id':'incident','events':[event]}
    (root/'in.json').write_text(json.dumps(request))
    subprocess.run(['python','/app/app/ledger.py',str(root/'state.db'),str(root/'in.json'),str(root/'out.json')], check=True)
    response = json.loads((root/'out.json').read_text())
    print('Observed:', response)
    assert response == {'watermarks':{'west':0}}, 'A missing prefix must not become billable'
