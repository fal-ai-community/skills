# fal.App configuration reference

Every option below is a class attribute on your `fal.App` subclass. Values are read
when the class is defined, on your machine, during `fal run` / `fal deploy`.

```python
import fal

class MyApp(fal.App):
    app_name = "my-app"                 # endpoint becomes <owner>/my-app
    app_auth = "private"                # used by `fal deploy`; `fal run` ignores it
    machine_type = ["GPU-H100", "GPU-A100"]
    num_gpus = 1
    requirements = ["torch==2.5.1", "diffusers==0.31.0"]
    keep_alive = 300
    min_concurrency = 0
    max_concurrency = 10
    max_multiplexing = 1
    startup_timeout = 900
    request_timeout = 600
    secrets = ["HF_TOKEN"]
```

## Environment

| Attribute | Type | Default | Notes |
|---|---|---|---|
| `requirements` | `list[str]` or `list[list[str]]` | `[]` | pip specifiers. A list of lists installs in several steps (e.g. `[["setuptools", "wheel"], ["my-pkg"]]`). Accepts wheel URLs, `pkg@https://...`, `--extra-index-url <url>` / `--find-links <url>` as separate items placed **before** the packages that need them, and `${SECRET_NAME}` placeholders resolved from fal secrets at build time. |
| `requirements_context_dir` | `str` | app file's directory | Base dir for local-path requirements such as `"."` or `"../shared[extra]"`. |
| `local_python_modules` | `list[str]` | `[]` | Local module names pickled with the app, e.g. `["my_utils"]`. |
| `app_files` | `list[str]` | `[]` | Local files/dirs uploaded with the app, e.g. `["./configs", "weights.json"]`. **Not allowed with `image`.** |
| `app_files_ignore` | `list[str]` | `.pyc`, `__pycache__/`, `.git/`, `.DS_Store` regexes | Regex patterns excluded from `app_files`. |
| `app_files_context_dir` | `str` | app file's directory | Base dir for `app_files`. Raises if set without `app_files`. |
| `image` | `ContainerImage` | `None` | Custom Docker image. Switches the app to container mode. See `containers.md`. |

Python version: the runner uses **your local interpreter's minor version** by default,
because the app is cloudpickled. There is no `python_version` class attribute (one is
silently ignored). Pin it with a class keyword, `class MyApp(fal.App, python_version="3.11")`,
or with `python_version = "3.11"` under `[tool.fal.apps.<name>]` in `pyproject.toml`.
Either way, deploy from a matching interpreter. A mismatch fails fast with
`Local Python X differs from the app's python_version=Y`.

## Hardware and placement

| Attribute | Type | Default | Notes |
|---|---|---|---|
| `machine_type` | `str` or `list[str]` | `"S"` | CPU: `XS`, `S`, `M`, `L`, `XL`. GPU: `GPU-A100`, `GPU-L40`, `GPU-H100`, `GPU-RTXPRO6000`, `GPU-H200`, `GPU-B200`. A list is a fallback order, tried until one has capacity. |
| `num_gpus` | `int` | `None` (server default) | GPUs per runner, GPU types only. |
| `regions` | `list[str]` | `None` (any) | `us-west`, `us-central`, `us-east`, `eu-north`, `eu-west`. |

Machine specs: https://fal.ai/docs/documentation/deployment/machine-types

## Scaling (see the fal-serverless-operate skill for tuning)

| Attribute | Default | Meaning |
|---|---|---|
| `keep_alive` | `60` | Seconds an idle runner stays warm. |
| `min_concurrency` | `0` | Runners always kept alive, even with no traffic (billed). |
| `max_concurrency` | `None` (server default 2) | Upper bound on runners. Set it explicitly. |
| `concurrency_buffer` | `0` | Extra warm runners above current demand. |
| `concurrency_buffer_perc` | `0` | Buffer as a percent of current request volume; the effective buffer is the max of this and `concurrency_buffer`. |
| `scaling_delay` | `0` | Seconds a request may wait before a scale-up is triggered. |
| `max_multiplexing` | `1` | Concurrent requests per runner. Raise only if handlers are `async` or otherwise concurrency-safe and the model has memory headroom. |
| `request_timeout` | platform default | Max seconds per request. On timeout the request is aborted and the runner is stopped. |
| `startup_timeout` | 600 s | Max seconds for runner start + `setup()`. `fal run` prints a warning if `setup()` exceeded it. |
| `termination_grace_period_seconds` | `5` (max 3600) | Budget between SIGTERM and SIGKILL, shared by in-flight requests and `teardown()`. Billed. |

These can also be passed as class keyword arguments:
`class MyApp(fal.App, keep_alive=300, max_concurrency=5): ...`

**Redeploy pitfall:** `keep_alive`, `min_concurrency`, `max_concurrency`,
`concurrency_buffer`, `concurrency_buffer_perc`, `scaling_delay`, `request_timeout` and
`regions` are inherited from the previous deployment on every `fal deploy`. Editing
them in code does nothing on a redeploy unless you pass `fal deploy --reset-scale`.
`machine_type`, `max_multiplexing` and `startup_timeout` always come from code.

## Access, identity, secrets, storage

| Attribute | Type | Notes |
|---|---|---|
| `app_name` | `str` | Defaults to the class name in kebab-case (`TextToImage` -> `text-to-image`). CLI `--app-name` overrides it. |
| `app_auth` | `"private"` / `"public"` / `"shared"` | `private`: only your account/team with a key. `public`: anyone, billed to you. `shared`: any authenticated caller, billed to the caller (needs account enablement). `fal deploy` defaults to `private`. |
| `secrets` | `list[str]` | Allowlist of secret **names** injected as env vars. Omitted: account default (usually all secrets). `[]`: none. Needs fal >= 1.72.3. |
| `data_mounts` | `list[str]` | Persistent paths to mount, e.g. `["/data"]` or `["/data/.cache"]`. Omitted: server default. |

## Reliability

| Attribute | Type | Notes |
|---|---|---|
| `skip_retry_conditions` | `list[str]` | Any of `"timeout"`, `"server_error"`, `"connection_error"`. Disables the platform's automatic retry for those. |
| `retry_config` | `dict` or `fal.sdk.RetryConfig` | Retry budget per condition, e.g. `{"server_error": {"retries": 3}}` or `RetryConfig(server_error=3, timeout=1)`. |

Health checks are declared on an endpoint, not as an attribute; see
`streaming-realtime-health.md`.

## Lifecycle hooks (methods, not attributes)

| Method | When it runs |
|---|---|
| `setup(self)` | Once per runner, before any request. May be `async`. Load models here. |
| `handle_exit(self)` | Immediately on SIGTERM. Signal long handlers to stop. |
| `teardown(self)` | After in-flight requests finish, inside the grace period. |
| `health(self)` | Backs the built-in `GET /health` route; returns `{"version": ...}` by default. |

Never override `__init__`: defining one raises `App classes should not override __init__ directly. Use setup() instead.`

`self.current_request` (inside a handler) exposes `request_id`, `endpoint`, `headers` and
`lifecycle_preference` for the current call.

## pyproject.toml (`[tool.fal.apps]`)

Name apps once and run them by name:

```toml
[tool.fal.apps.my-app]
ref = "src/app.py::MyApp"          # or python_entry_point = "my_pkg.server:MyApp"
auth = "private"
machine_type = "GPU-H100"
python_version = "3.11"
keep_alive = 300
max_concurrency = 5
secrets = ["HF_TOKEN"]
app_scale_settings = true           # like --reset-scale on every deploy
```

```bash
fal run my-app
fal deploy my-app
```

- `ref` paths resolve from the directory containing `pyproject.toml`.
- Also accepted: `name`, `team`, `deployment_strategy` (`rolling`/`recreate`),
  `requirements`, `requirements_context_dir`, `num_gpus`, `regions`, all scaling keys,
  `private_logs`, `app_files`, `app_files_ignore`, `app_files_context_dir`,
  `exposed_port`, `skip_retry_conditions`, `retry_config`,
  `termination_grace_period_seconds`, `data_mounts`, `health_check` (table) and
  `image` (table). Unknown keys are rejected.
- `no_scale` is deprecated; use `app_scale_settings`.
- With `python_entry_point`, runtime settings come from `pyproject.toml`, not from
  class attributes in the imported package.
- `fal deploy <name>` honours `auth` from the file. `fal run <name>` still defaults to
  `public` unless you pass `--auth`.
- `fal deploy <name>` rejects `--app-name` and `--auth`; set `name` / `auth` in the
  file instead. The strategy and scale-reset behaviour also come from the file
  (`deployment_strategy`, `app_scale_settings`): with an app-name reference the
  `--strategy` and `--reset-scale` flags are replaced by the file's values, so set them
  there. Deploy by file reference (`fal deploy src/app.py::MyApp --reset-scale`) when you
  need the flags.

Full schema: https://fal.ai/docs/api-reference/python-sdk/pyproject-toml
