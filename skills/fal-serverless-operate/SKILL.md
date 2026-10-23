---
name: fal-serverless-operate
description: Operate and debug your own apps already deployed on fal Serverless with the `fal` CLI. Covers listing apps and revisions, rollback (`fal apps set-rev`), restarting runners (`fal apps rollout`), scaling (`fal apps scale` for keep_alive, min/max concurrency, machine types), runner states (PENDING, SETUP, CRASH_BACKOFF), logs (`fal runners logs`), shells on runners, the queue, and secrets, keys, environments and /data files. Also diagnoses crash loops, 5xx/503/504 errors, timeouts and cold starts. Use when the user says "fal logs", "fal runners", "my fal app is failing", "roll back on fal", "scale my fal app", "cold start", "keep_alive", "fal apps", "fal queue", "fal secrets", or asks why a deployed fal endpoint is slow, erroring or expensive. This skill covers your own deployed apps and the `fal` CLI. It is not for calling fal marketplace models (the genmedia CLI does that). To write or first deploy an app, use fal-serverless.
---

# Operating fal Serverless apps

All commands below are `fal` CLI commands (`pip install fal`). Names in examples
(`my-app`, `my-org`) are placeholders. `app_name` arguments are the app name **without**
the owner prefix. For exact flags, run `fal <command> --help`; it always matches the
installed version.

## Safety: confirm with the user before running

These are destructive, disruptive or billed:
`fal deploy` (over an existing app, or with `--yes`), `fal apps set-rev`,
`fal apps rollout`, `fal apps delete`, `fal apps delete-rev`, `fal environments delete`
(removes all its apps, secrets and history), `fal queue flush`, `fal runners kill`/`stop`,
`fal keys revoke`, `fal secrets set` over an existing name (the old value is gone),
`fal secrets unset`, `fal files rm`, `fal run` (bills until stopped), and `fal apps scale`
raising `--min-concurrency` or `--concurrency-buffer` (runners billed around the clock)
or changing machine types.

## 0. Establish context first

```bash
fal auth whoami                 # the account in use; `fal account set <team>` to switch
fal apps list                   # add --env staging to look outside `main`
```

- Every app lives in one environment, and most `fal apps` commands, `deploy`, `run` and
  `secrets` take `--env <name>` (default `main`). Forget it and you will be looking at the
  wrong app. `fal queue` has no `--env` and acts on the app in `main`; do not use it for
  another environment.
- A key (`FAL_KEY`, or `FAL_KEY_ID`/`FAL_KEY_SECRET`) overrides the login session: with
  one set, `--team` and `fal account set` are ignored. `fal auth whoami` is the
  definitive check.

## 1. Inspect state

```bash
fal apps runners my-app                             # live runners and their states
fal apps runners my-app --since 1h --state all      # include terminated runners
fal queue size my-app                               # queued requests
fal apps list-rev my-app                            # revisions
```

Runner states: `PENDING` (waiting for hardware), `DOCKER_PULL`, `SETUP` (in `setup()`),
`IDLE`, `RUNNING`, `DRAINING`, `TERMINATING`, `TERMINATED`, and `CRASH_BACKOFF` (a
previous start failed, so the next one is delayed).

## 2. Read logs

```bash
fal runners logs <runner_id> --lines 200
fal runners logs <runner_id> --since 30m --search Traceback
```

Logs are per runner. Find the id with `fal apps runners`, and use `--since` to reach
runners that already died. The dashboard Logs page filters across runners by request.

## 3. Get onto the machine

```bash
fal runners exec <runner_id> -- nvidia-smi
fal runners exec <runner_id> -- ls -lh /data/models
```

Put `--` before the command so its flags are not parsed as `fal` flags. Run one-shot
commands; an interactive session needs the user's terminal. Never print secret values
(`env`, `echo $HF_TOKEN`) from a runner.

## 4. Fix and recover

| Situation | Command |
|---|---|
| Bad deploy: go back | `fal apps list-rev my-app`, then `fal apps set-rev my-app <rev_id> --strategy rolling` |
| Restart all runners (after a secret change, leaked memory, bad state) | `fal apps rollout my-app` (graceful); `--force` kills immediately and drops in-flight requests |
| Replace one runner | `fal runners stop <id> --replace` (graceful); `fal runners kill <id>` (immediate) |
| Redeploy a fix | `fal deploy app.py::MyApp --message "fix oom"` |
| Review what a deploy will change | `fal deploy app.py::MyApp --check`; in a non-interactive shell it prints the diff and exits without deploying. Show it to the user before adding `--yes` |
| Drop a backlog | `fal queue flush my-app` |

A rolling deploy switches traffic only after a runner on the new revision passes
`setup()`; if it crashes, traffic stays on the old revision. `fal deploy --detach` skips
that protection, and so does `--attach`: leave both out for a fix whose `setup()` is
untested.

## 5. Scale and tune (no redeploy)

```bash
fal apps scale my-app --min-concurrency 1 --max-concurrency 20 --keep-alive 300
fal apps scale my-app --machine-types GPU-H100 GPU-A100 && fal apps rollout my-app
```

- Values set here (scaling, `request_timeout`, regions) **stick across future deploys**. To go back to the values in
  code, deploy with `--reset-scale`. `machine_type`, `max_multiplexing` and
  `startup_timeout` are the exception: the next deploy resets them to the code.
- Machine type changes affect only new runners; follow them with `fal apps rollout`.
- Billing covers every second a runner is in `SETUP`, `IDLE` (including `keep_alive`),
  `RUNNING`, `DRAINING` or `TERMINATING`. `min_concurrency` and `concurrency_buffer`
  keep runners up, and billed, even with no traffic.

## 6. Secrets and keys

Ask the user to set or rotate secret values themselves (`fal secrets set NAME=<value>`
in their own terminal, or the dashboard); never put a real value in a command you run.
`fal secrets list` shows names only. Re-setting a secret that was set with
`--not-exposed-by-default` needs that flag again, or it becomes exposed to every app
without a `secrets` list. Runners read secrets at start, so follow a change with
`fal apps rollout my-app`. Secrets do not fall back between environments.

Keys are created by the user with `fal keys create --preset <PRESET>`: `API` to call
apps, `SERVERLESS` to build, deploy and run them. Do not suggest `--scope ADMIN`: it is
deprecated and makes a key with full access to the account, billing included. The key is
printed once.

## 7. Smoke-test an endpoint

```bash
fal api my-org/my-app prompt="hello"               # goes through the queue
```

Non-main environments add a suffix: `my-org/my-app--staging`.

## Diagnose from the symptom

| Symptom | Likely cause | Check or fix |
|---|---|---|
| Runners loop SETUP to CRASH_BACKOFF | exception in `setup()`, OOM, missing package or secret, `startup_timeout` too low | `fal runners logs <id>`; reproduce with `fal run app.py::MyApp --auth private` and stop it when done |
| Long PENDING | no capacity for that GPU or region, or the account's GPU limit is reached | `fal runners gpus` shows GPUs in use (not the limit); add fallback machine types, or scale down other apps |
| Every error kills its runner | the app returns 503 | return 500 or 4xx; 503 means "runner broken" |
| 504 on long requests | work exceeds `request_timeout` | `fal apps scale my-app --request-timeout N` (a code change needs `--reset-scale`), or set `skip_retry_conditions=["timeout"]` on the app so timeouts are not retried |
| First request after idle is slow | runners expired | raise `keep_alive`, add `min_concurrency`, speed up `setup()` |
| Scaling changes in code ignored | live values are inherited | `fal deploy app.py::MyApp --reset-scale` |
| New secret value not seen | runners started before the change | `fal apps rollout my-app` |
| 401/403 calling the app | private app, or a key from another account | `fal auth whoami`; check the environment suffix in the app id |

## Docs

- Managing deployments and rollbacks: https://fal.ai/docs/documentation/deployment/manage-deployments,
  https://fal.ai/docs/documentation/deployment/rollbacks
- Runners and debugging: https://fal.ai/docs/documentation/deployment/runners,
  https://fal.ai/docs/documentation/deployment/debug-runners,
  https://fal.ai/docs/documentation/serverless/observability/logs
- Scaling, cold starts and cost: https://fal.ai/docs/documentation/deployment/scale-your-application,
  https://fal.ai/docs/documentation/serverless/optimizations/optimize-cold-starts,
  https://fal.ai/docs/documentation/serverless/optimizations/optimizing-costs,
  https://fal.ai/docs/documentation/serverless/pricing
- Retries: https://fal.ai/docs/documentation/serverless/reliability/retries
- Debugging from an agent (Platform MCP): https://fal.ai/docs/documentation/serverless/observability/debug-with-ai
