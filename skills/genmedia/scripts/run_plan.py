#!/usr/bin/env python3
"""Run one reviewed genmedia stage; persist submissions before any status polling."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def load_plan(path):
    plan = json.loads(Path(path).read_text(encoding='utf-8'))
    if plan.get('version') != 1 or not isinstance(plan.get('stages'), list):
        raise ValueError('Expected plan version 1 with stages')
    seen = set()
    for stage in plan['stages']:
        name = stage.get('id', '')
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', name) or name in seen:
            raise ValueError('Stage IDs must be unique safe names')
        seen.add(name)
        endpoint = stage.get('endpoint', '')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+', endpoint):
            raise ValueError('Invalid endpoint')
        if not isinstance(stage.get('inputs'), dict) or not stage['inputs']:
            raise ValueError('Inputs must be a nonempty object')
        for key in stage['inputs']:
            if not re.fullmatch(r'[a-z][a-z0-9_]*', key):
                raise ValueError('Invalid input parameter')
        if not isinstance(stage.get('async', True), bool):
            raise ValueError('async must be boolean')
    return plan


def command(stage, download):
    args = ['genmedia', 'run', stage['endpoint']]
    for key, value in stage['inputs'].items():
        if key in {'json', 'async', 'download', 'help', 'timeout', 'no-wait'}:
            raise ValueError('Input collides with a runner option')
        encoded = value if isinstance(value, str) else json.dumps(value, separators=(',', ':'))
        args += ['--' + key, encoded]
    args += ['--json']
    if stage.get('async', True):
        args += ['--async']
    else:
        args += ['--download', str(download) + '/']
    return args


def call(args):
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def save(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')
    temp.replace(path)


def run(plan_path, stage_id, state, execute=False, poll=False, invoke=call):
    plan = load_plan(plan_path)
    stage = next((s for s in plan['stages'] if s['id'] == stage_id), None)
    if stage is None:
        raise ValueError('Unknown stage')
    digest = hashlib.sha256(json.dumps(stage, sort_keys=True).encode()).hexdigest()
    state = Path(state)
    cmd = command(stage, state / (stage_id + '-files') / '')
    if not execute and not poll:
        return {'dry_run': True, 'stage': stage_id, 'argv': cmd}
    if 'REPLACE_' in json.dumps(stage):
        raise ValueError('Replace example inputs before execution')
    state.mkdir(parents=True, exist_ok=True)
    record_path = state / (stage_id + '.json')
    lock = state / (stage_id + '.lock')
    # Exclusive lock prevents two agents from submitting the same stage together.
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.close(fd)
        if poll:
            record = json.loads(record_path.read_text(encoding='utf-8'))
            if record['digest'] != digest:
                raise ValueError('Stage changed: reconcile saved request before continuing')
            if record.get('phase') == 'complete':
                return record
            req = record.get('submission', {}).get('request_id')
            if not req:
                raise ValueError('No saved request ID: reconcile the uncertain submission manually')
            result = invoke(['genmedia', 'status', stage['endpoint'], req, '--result',
                             '--download', str(state / (stage_id + '-files')) + '/', '--json'])
            record['last_status'] = result
            # Keep polling possible on queue/progress responses. Do not claim completion.
            if result.get('status') == 'COMPLETED' or result.get('downloaded_files'):
                record['phase'] = 'complete'
            save(record_path, record)
            return record
        if record_path.exists():
            raise ValueError('Stage already attempted: use --poll or reconcile it manually')
        preflight = {}
        for action in ['schema', 'pricing']:
            preflight[action] = invoke(['genmedia', action, stage['endpoint'], '--json'])
        record = {'digest': digest, 'stage': stage_id, 'endpoint': stage['endpoint'],
                  'phase': 'submitting', 'preflight': preflight}
        save(record_path, record)
        # Never retry this call automatically: the server may charge before a lost response.
        (state / (stage_id + '-files')).mkdir(exist_ok=True)
        result = invoke(cmd)
        record['submission'] = result
        record['phase'] = 'submitted' if stage.get('async', True) else 'complete'
        save(record_path, record)
        return record
    finally:
        lock.unlink()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('plan')
    p.add_argument('--stage', required=True)
    p.add_argument('--state', default='./production-state')
    modes = p.add_mutually_exclusive_group()
    modes.add_argument('--execute', action='store_true')
    modes.add_argument('--poll', action='store_true')
    args = p.parse_args()
    try:
        print(json.dumps(run(args.plan, args.stage, args.state, args.execute, args.poll), indent=2))
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        p.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
