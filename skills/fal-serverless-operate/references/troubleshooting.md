# Troubleshooting deployed fal apps

## Runner states

| State | Meaning | Billed |
|---|---|---|
| `PENDING` | Waiting for hardware. Long PENDING means capacity is short: add fallback machine types or regions. | no |
| `DOCKER_PULL` | Pulling the image (skipped when cached on the node). | no |
| `SETUP` | Running `setup()`. | yes |
| `IDLE` | Ready, no requests. Includes the `keep_alive` window. | yes |
| `RUNNING` | Serving one or more requests. | yes |
| `DRAINING` | Finishing in-flight requests, accepting no new ones. | yes |
| `TERMINATING` | Shutting down, running `teardown()`. | yes |
| `TERMINATED` | Gone. Visible for 24 h with `--since`. | no |
| `CRASH_BACKOFF` | A previous start failed; this start is delayed before retrying. | not stated in docs |

Startup failures (a crash in `setup()`, a `startup_timeout` overrun) add a growing delay
to every later start of that app: 30 s, 60 s, 90 s, and so on, capped at 10 minutes.
The delay resets as soon as any runner starts successfully. Scheduling failures (no
hardware) wait a fixed 20 s instead.

Filter with `--state` (lowercase): `idle`, `running`, `pending`, `setup`,
`crash_backoff`, `terminated`, `all`.

## Triage by symptom

**App keeps restarting or never becomes ready (SETUP to CRASH_BACKOFF loop)**
1. `fal apps runners my-app --since 1h --state all --json` and pick a failed runner id.
2. `fal runners logs <id> --lines 200` and look for the traceback at the end of `setup()`.
3. Usual causes:
   - `ModuleNotFoundError`: a package is missing from `requirements`, or an import at
     module top level needs a package the runner lacks.
   - CUDA/torch mismatch: unpinned `torch`, or the wrong `--extra-index-url`.
   - OOM while loading: the model is too big for the GPU. Use a bigger `machine_type`
     or fp16.
   - `setup()` exceeded `startup_timeout` (600 s default) on the first weight download:
     raise `startup_timeout` or pre-stage weights on `/data`.
   - A secret is missing: `os.environ[...]` raised `KeyError`. Check
     `fal secrets list --env <env>` and the app's `secrets` allowlist.
4. Reproduce with `fal run app.py::MyApp`, which runs the same `setup()` and streams its
   logs to your terminal.

**Requests fail with 500**
- Search the logs: `fal runners logs <id> --search Traceback --since 30m`.
- A 500 is returned to the caller and is not retried by default. The runner gets a
  health check and is replaced only if the check fails.

**Runners die after an error**
- The app returned 503, which stops the runner immediately. Reserve 503 for truly
  broken state, or send `x-fal-stop-runner: false` with it.
- The dashboard shows a termination reason next to each stopped runner (for example
  "Request timed out", "Health check failed", "Keep-alive expired", "Scaled down",
  "Runner crashed").

**Requests time out (504, `error_type: request_timeout`)**
- The app's `request_timeout` was exceeded. The runner is stopped because the work may
  still be running, and queue requests are retried. Raise the limit with
  `fal apps scale my-app --request-timeout 1800` (runtime-tunable), or add
  `skip_retry_conditions = ["timeout"]` so a slow request is not run up to 10 times.

**Requests wait a long time in the queue**
- `fal queue size my-app` (name without the owner) and `fal apps runners my-app --state pending setup`.
- Pending runners mean capacity: add `machine_type` fallbacks or more `regions`.
- Setup runners mean cold starts (see `cold-starts-and-cost.md`).
- Check `max_concurrency` is not the cap. Account concurrency limits do not apply to your
  own apps; `max_concurrency` does.
- Callers can set `start_timeout` so a request gives up (504) if it has not started.

**Stuck or bad runner**
- Inspect: `fal runners shell <id>`, or `fal runners exec <id> -- nvidia-smi`,
  `fal runners exec <id> -- ls -lh /data/models`, `fal runners exec <id> -- env`.
- Replace one: `fal runners stop <id> --replace` (graceful, replacement first) or
  `fal runners kill <id>` (immediate).
- Replace all: `fal apps rollout my-app` (graceful) or `--force` (drops in-flight work).

**Bad deploy**
- `fal apps list-rev my-app`, then `fal apps set-rev my-app <revision_id> --strategy rolling`.
  Runtime scaling values stay as they are live; `machine_type`, `max_multiplexing` and
  `startup_timeout` come from the target revision's code.

**Deploy fails before a runner starts**
- `Local Python X differs from the app's python_version=Y`: deploy from a matching
  interpreter or change `python_version`.
- `App classes should not override __init__ directly`: move the code into `setup()`.
- `app_files is not supported for container apps.`: use `COPY` in the Dockerfile.
- Build errors: rerun with `--no-cache`, and add `--debug` for the full traceback.
- `fal doctor` prints the fal version and which key is active.

## Status codes and retries

| App returns | Runner | Queue retry |
|---|---|---|
| 2xx, 3xx, 4xx | kept | no (3xx goes back to the caller unfollowed) |
| 500, 502 | health-checked, replaced if the check fails | no |
| 503 | stopped immediately | yes |
| 504 | health-checked | yes |

- Queue requests (`submit`/`subscribe`) are retried on another runner, up to 10 attempts,
  after 503, 504, runner crashes and connection failures. Direct `run()`/`stream()`
  calls are never retried: a crash returns 503 and a timeout returns 504.
- App controls: `skip_retry_conditions` (`timeout`, `server_error`, `connection_error`)
  and `retry_config` (`{"server_error": {"retries": 3}}`; `retries` counts extra attempts).
- Response headers: `X-Fal-Needs-Retry: 1|0` (honoured only on 5xx and 429),
  `x-fal-stop-runner: true|false`.
- Caller headers: `x-fal-no-retry: 1`, `X-Fal-Retry-Config: <json>` (own apps only).
  `x-fal-no-retry` wins if both are sent.

Platform error bodies carry `detail` and `error_type` (also in the `X-Fal-Error-Type`
header):

| `error_type` | Typical status |
|---|---|
| `request_timeout`, `startup_timeout` | 504 |
| `runner_scheduling_failure`, `runner_connection_timeout`, `runner_disconnected`, `runner_connection_refused`, `runner_connection_error` | 503 |
| `runner_incomplete_response` | 502 |
| `runner_server_error`, `internal_error` | 500 |
| `client_disconnected`, `client_cancelled` | 499 |
| `bad_request` | 400 |

## Timeouts at a glance

| Timeout | Set by | Scope | On expiry |
|---|---|---|---|
| `request_timeout` | app (default 3600 s) | one request's processing | runner stopped; queue retry (`timeout` condition) |
| `startup_timeout` | app | runner start plus `setup()` | runner replaced; request stays queued |
| `start_timeout` (`X-Fal-Request-Timeout`) | caller | wall clock until processing starts, across retries | 504, no retry |
| `client_timeout` | caller (Python SDK) | client wait only | client stops waiting; the server may still run it |

## Logs

- Runner logs cover the whole runner lifetime. Only the owner can see them, via
  `fal runners logs <id>` or the dashboard Logs page (filter by runner, request,
  revision, endpoint, level).
- Request logs (the slice during a request) are visible to **callers** polling with
  `with_logs=True`. Never print secrets or user data. Hide them with
  `class MyApp(fal.App, private_logs=True)` or the account-wide setting.
- The request id is `self.current_request.request_id` inside a handler. Log it to
  correlate with caller reports.
- Log drains and a Prometheus-compatible metrics API exist for shipping to your own stack:
  https://fal.ai/docs/documentation/serverless/observability/log-drains

Docs:
- https://fal.ai/docs/documentation/deployment/runners
- https://fal.ai/docs/documentation/deployment/debug-runners
- https://fal.ai/docs/documentation/serverless/reliability/retries
- https://fal.ai/docs/documentation/serverless/observability/logs
