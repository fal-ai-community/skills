---
name: fal-serverless-operate
description: Operate and debug your own apps already deployed on fal Serverless with the `fal` CLI. Covers listing apps and revisions, rollback (`fal apps set-rev`), restarting runners (`fal apps rollout`), scaling (`fal apps scale` for keep_alive, min/max concurrency, machine types), runner states (PENDING, SETUP, CRASH_BACKOFF), logs (`fal runners logs`), shells on runners, the queue, and secrets, keys, environments and /data files. Also diagnoses crash loops, 5xx/503/504 errors, timeouts and retries, and cuts cold starts and GPU cost. Use when the user says "fal logs", "fal runners", "my fal app is failing", "roll back on fal", "scale my fal app", "cold start", "keep_alive", "fal apps", "fal queue", "fal secrets", "fal doctor", or asks why a deployed fal endpoint is slow, erroring or expensive. This skill covers your own deployed apps and the `fal` CLI. It is not for calling fal marketplace models (the genmedia CLI does that). To write or first deploy an app, use fal-serverless.
---

# Operating fal Serverless apps

All commands below are `fal` CLI commands (`pip install fal`). Names in examples
(`my-app`, `my-org`) are placeholders. `app_name` arguments are the app name **without**
the owner prefix.

## 0. Establish context first

```bash
fal auth whoami                 # who am I; `fal account list` / `fal account set <team>` to switch
fal doctor                      # fal version + key id from the FAL_KEY env var (blank otherwise)
fal apps list                   # add --env staging to look outside `main`
```

- Every app lives in one environment. `fal apps {list,list-rev,scale,rollout,set-rev,runners,delete}`,
  `deploy`, `run` and `secrets` take `--env <name>` (or `FAL_ENV`; default `main`). Forget
  it and you will be looking at the wrong app. `queue`, `runners`, `apps gpus`,
  `apps delete-rev`, `api` and `files` have no environment flag.
- Commands that talk to the platform take `--team <team>`; list and inspect commands
  (and `deploy`) take `--json`. Check `fal <cmd> --help` before relying on either flag.
- A `FAL_KEY` env var overrides the login session. Check `fal doctor` if results look
  like another account's.

## 1. Inspect state

```bash
fal apps runners my-app                             # live runners and their states
fal apps runners my-app --since 1h --state all      # include terminated runners (max 24 h)
fal apps runners my-app --state pending setup crash_backoff
fal runners list --state running                    # across all apps
fal queue size my-app                               # queued requests (--by-user to split)
fal apps list-rev my-app                            # revisions (id, date, machine, scaling)
fal apps gpus my-app
```

Runner states: `PENDING` (waiting for hardware), `DOCKER_PULL`, `SETUP` (in `setup()`),
`IDLE`, `RUNNING`, `DRAINING`, `TERMINATING`, `TERMINATED`, and `CRASH_BACKOFF` (a
previous start failed, so the next one is delayed 30 s, 60 s, ... up to 10 min).

## 2. Read logs

```bash
fal runners logs <runner_id> --lines 200            # latest 200 lines
fal runners logs <runner_id> --since 30m --search Traceback
fal runners logs <runner_id> --follow               # live tail
fal runners logs <runner_id> --json                 # structured output
```

Logs are per runner. Find the id with `fal apps runners`, and use `--since` to reach
runners that already died. The dashboard Logs page filters across runners by request
id, revision and endpoint. Nothing in the CLI shows app-wide logs in one stream.

## 3. Get onto the machine

```bash
fal runners shell <runner_id>                       # interactive shell in the container
fal runners exec <runner_id> -- nvidia-smi
fal runners exec <runner_id> -- ls -lh /data/models
fal runners exec <runner_id> -it -- python
```

Put `--` before the command so its flags are not parsed as `fal` flags.

## 4. Fix and recover

| Situation | Command |
|---|---|
| Bad deploy: go back | `fal apps list-rev my-app` then `fal apps set-rev my-app <rev_id> --strategy rolling` |
| Restart all runners (after a secret change, leaked memory, bad state) | `fal apps rollout my-app` (graceful); `--force` kills immediately and drops in-flight requests |
| Replace one runner | `fal runners stop <id> --replace` (graceful, replacement first); `fal runners kill <id>` (immediate) |
| Redeploy a fix | `fal deploy app.py::MyApp --message "fix oom"` |
| Preview what a deploy will change | `fal deploy app.py::MyApp --check` (add `--yes` in CI) |
| Deploy without waiting for the rollout | `fal deploy ... --detach` (rolling only) |
| Switch traffic instantly (next request cold-starts) | `--strategy recreate` on `deploy` or `set-rev` |
| Drop a backlog | `fal queue flush my-app` (optionally `--caller-user-id <id>`) |

A rolling deploy or `set-rev --strategy rolling` starts one runner on the new revision
and switches traffic only after its `setup()` passes. If `setup()` crashes, traffic stays
on the old revision.

## 5. Scale and tune (no redeploy)

```bash
fal apps scale my-app --min-concurrency 1 --max-concurrency 20 --keep-alive 300
fal apps scale my-app --concurrency-buffer 2 --scaling-delay 15
fal apps scale my-app --request-timeout 1800 --startup-timeout 1200
fal apps scale my-app --machine-types GPU-H100 GPU-A100 && fal apps rollout my-app
```

- Runtime-tunable values (`keep_alive`, `min/max_concurrency`, `concurrency_buffer[_perc]`,
  `scaling_delay`, `request_timeout`, `regions`) **stick across future deploys**. To go
  back to code values, deploy with `fal deploy app.py::MyApp --reset-scale`. A pyproject
  name reference ignores that flag; set `app_scale_settings = true` in the app's table.
- `machine_type`, `max_multiplexing` and `startup_timeout` set here are temporary: the
  next deploy resets them to the code. Machine type changes affect only new runners;
  follow them with `fal apps rollout`.
- Billing covers every live second of `SETUP`, `IDLE` (including `keep_alive`),
  `RUNNING`, `DRAINING` and `TERMINATING` (`teardown()`). `PENDING`, `DOCKER_PULL` and
  `TERMINATED` are free. `min_concurrency`
  runners bill around the clock.

Tuning recipes and cold-start fixes: `references/cold-starts-and-cost.md`.

## 6. Secrets, keys, environments, files

```bash
fal secrets set HF_TOKEN=hf_xxx --env main      # then `fal apps rollout my-app`: runners read secrets at start
fal secrets list --env staging                  # names only, never values
fal secrets unset OLD_TOKEN

fal keys create --scope API --desc "prod caller"   # call any model or app + API-scoped Platform APIs; cannot deploy/manage; prints FAL_KEY='id:secret' ONCE
fal keys create --scope ADMIN --desc "CI deploys"  # also needed for fal deploy / fal run / managing apps
fal keys list
fal keys revoke <key_id>

fal environments list
fal environments create staging --description "pre-prod"

fal files list models/                          # the account's /data volume
fal files upload ./weights.safetensors models/weights.safetensors
fal files download models/config.json ./config.json
```

Secrets do not fall back between environments. `fal files upload` will not overwrite an
existing path; `fal files rm` it first.

## 7. Smoke-test an endpoint

```bash
fal api my-org/my-app prompt="hello"               # goes through the queue
curl -X POST https://fal.run/my-org/my-app \
  -H "Authorization: Key $FAL_KEY" -H "Content-Type: application/json" -d '{"prompt":"hello"}'
```

Non-main environments add a suffix: `my-org/my-app--staging`.

## Diagnose from the symptom

| Symptom | Likely cause | Check or fix |
|---|---|---|
| Runners loop SETUP to CRASH_BACKOFF | exception in `setup()`, OOM, missing package or secret, `startup_timeout` too low | `fal runners logs <id>`; reproduce with `fal run app.py::MyApp` |
| Long PENDING | no capacity for that GPU or region | add fallback `machine_type`s or regions |
| Every error kills its runner | the app returns 503 | return 500 or 4xx; 503 means "runner broken" |
| 504 `request_timeout` | work exceeds `request_timeout` | raise it, or set `skip_retry_conditions=["timeout"]` so it is not retried 10 times |
| First request after idle is slow | runners expired | raise `keep_alive`, add `min_concurrency` or `concurrency_buffer`, speed up `setup()` |
| Code scaling changes ignored | inherited live values | `fal deploy app.py::MyApp --reset-scale` (by app name: `app_scale_settings = true` in pyproject) |
| New secret value not seen | runners started before the change | `fal apps rollout my-app` |
| 401/403 calling the app | private app, or a key from another account/team | `fal auth whoami`, `fal keys list` (a wrong `--<env>` suffix points at a different or missing app; check the alias) |

Status-code semantics, retry headers, error types and timeouts:
`references/troubleshooting.md`.

## Safety: confirm with the user before running

These are destructive or disruptive and cannot be undone:
`fal apps delete`, `fal apps delete-rev`, `fal environments delete` (removes all its
apps, secrets and history), `fal queue flush`, `fal apps rollout --force`,
`fal runners kill`, `fal keys revoke`, `fal secrets unset`, `fal files rm` (recursive),
and `fal apps scale my-app --min-concurrency 1` (any N > 0 starts billing N runners
around the clock).

## Platform MCP (optional)

fal documents a read-only Platform MCP server for operating apps from an agent. It
exposes tools such as `list_apps`, `fetch_requests`, `fetch_request_logs`,
`get_analytics`, `fetch_events`, `list_revisions`, `get_current_state`,
`get_runner_history` and `get_usage` (admin key). Note that it uses the `Key` auth scheme:

```bash
claude mcp add --transport http fal-platform https://api.fal.ai/v1/mcp/platform \
  --header "Authorization: Key $FAL_KEY"
```

https://fal.ai/docs/documentation/serverless/observability/debug-with-ai

## References

- `references/cli-reference.md`: read when you need the exact flags of any `fal` command
  (apps, runners, deploy, run, queue, secrets, keys, environments, files, api).
- `references/troubleshooting.md`: read when diagnosing failures. Covers runner states,
  status codes and retries, `error_type` values, timeouts and logs.
- `references/cold-starts-and-cost.md`: read when tuning latency or spend. Covers
  billing rules, the scaling knobs, recipes and faster `setup()`.

Public docs:
- https://fal.ai/docs/documentation/deployment/manage-deployments
- https://fal.ai/docs/documentation/deployment/rollbacks
