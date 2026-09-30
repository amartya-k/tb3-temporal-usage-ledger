"""Stage local trajectory-review tasks with the current upstream prompts/model.

Upstream hosted staging downloads public Harbor trials. Our trials are local
Docker runs, so only the evidence transport changes: the downloaded Actions
artifact and exact source task are copied into the reviewer image instead.
"""
import argparse
import importlib.util
import json
import shutil
import tomllib
from pathlib import Path
import yaml
from evaluate import ROOT, UPSTREAM, TASK, run


def stage(trial, task, destination):
    spec = importlib.util.spec_from_file_location('upstream_staging', UPSTREAM / 'scripts/ci/stage_hosted_analysis.py')
    upstream = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(upstream)
    criteria = tomllib.loads((UPSTREAM / 'docs/prompts/trial-analysis.toml').read_text())['criteria']
    guidance = '\n\n'.join(f"{c['name']}: {c['description']}\n{c['guidance']}" for c in criteria)
    environment, tests = destination / 'environment', destination / 'tests'
    environment.mkdir(parents=True)
    tests.mkdir()
    shutil.copytree(trial, environment / 'trial')
    shutil.copytree(task, environment / 'task')
    (environment / 'Dockerfile').write_text('FROM python:3.12-slim-bookworm\nRUN apt-get update && apt-get install -y --no-install-recommends ca-certificates git jq && rm -rf /var/lib/apt/lists/*\nCOPY trial /app/trial\nCOPY task /app/task\nWORKDIR /app\n')
    (tests / 'criteria.json').write_text(json.dumps([c['name'] for c in criteria]))
    (tests / 'validate.jq').write_text(upstream.VALIDATE_JQ)
    (tests / 'test.sh').write_text(upstream.VERIFIER)
    (tests / 'Dockerfile').write_text('FROM python:3.12-slim-bookworm\nRUN apt-get update && apt-get install -y --no-install-recommends jq && rm -rf /var/lib/apt/lists/*\nCOPY . /tests/\nRUN mkdir -p /app /logs/verifier\n')
    (destination / 'instruction.md').write_text((UPSTREAM / 'docs/prompts/trial-analysis.txt').read_text() + '\n\n' + guidance)
    (destination / 'task.toml').write_text('schema_version = "1.3"\nartifacts = [{ source = "/app/analysis.json", destination = "analysis.json" }]\n[agent]\ntimeout_sec = 600.0\n[verifier]\nenvironment_mode = "separate"\ntimeout_sec = 30.0\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('source_repo', type=Path)
    parser.add_argument('--stage-only', action='store_true')
    args = parser.parse_args()
    defaults = yaml.safe_load((UPSTREAM / '.github/harbor-run-defaults.yml').read_text())
    trials = [p.parent for p in sorted(args.evidence.rglob('result.json')) if (p.parent / 'agent/trajectory.json').is_file()]
    if not trials:
        raise SystemExit('No recorded agent trajectories in supplied artifacts')
    for index, trial in enumerate(trials):
        output = ROOT / 'analysis-tasks' / f'trial-{index}'
        stage(trial, args.source_repo / TASK, output)
        print(f'Staged {trial.name}', flush=True)
        if not args.stage_only:
            entry = dict(id=f'analysis-{index}', kind='analysis', agent=defaults['analyze_agent'], model=defaults['analyze_model'], kwargs={}, env={})
            run(entry, task_override=output)


if __name__ == '__main__':
    main()
