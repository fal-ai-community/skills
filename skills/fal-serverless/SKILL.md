---
name: fal-serverless
description: Build, test and deploy your own Python apps on fal Serverless GPUs with the `fal` SDK and CLI. Covers writing a `fal.App` (setup(), `@fal.endpoint`, Pydantic input/output, requirements, machine_type such as GPU-H100, keep_alive / min_concurrency / max_concurrency, secrets, fal.toolkit Image/File uploads, /data persistent storage, custom ContainerImage or Dockerfile, streaming and realtime endpoints, pyproject `[tool.fal.apps]`), testing with `fal run`, shipping with `fal deploy`, and calling the endpoint via fal_client, curl or the queue. Use when the user says "deploy to fal", "fal.App", "fal run", "fal deploy", "serverless GPU app on fal", "host my model on fal", "fal.endpoint", "machine_type", or edits code that imports `fal`. This skill is for building and hosting your own apps with the `fal` CLI. It is not for calling existing fal marketplace models (that is the genmedia CLI). For debugging, scaling or operating an app that is already deployed, use fal-serverless-operate.
---

# fal Serverless: build and deploy a fal.App

You write a Python class that subclasses `fal.App`. `fal run` boots it on a temporary
cloud runner for testing, and `fal deploy` makes it a persistent, autoscaling HTTP/queue
endpoint at `<owner>/<app-name>`. Builds happen remotely, so no local Docker or GPU is
needed.

## Setup

```bash
pip install fal            # the SDK + CLI (also install it in the project's venv)
fal auth whoami            # which account is in use
```

If `whoami` fails, ask the user to authenticate. The simplest path from an agent shell
is for the user to export `FAL_KEY` themselves, or to run `fal auth login` in their own
terminal (it prompts for a login method, then for an account). If you run it yourself,
it blocks polling until the browser step completes and then asks for an account, so run
it in the background with that answer piped in, and read the URL from the log:

```bash
printf '\n' | fal auth login --connection github --no-browser > fal-login.log 2>&1 &
# (or google, or their SSO domain); the empty line picks the default account
```

Give the user the URL from `fal-login.log`, wait for the job to exit, then re-check
`fal auth whoami`. Never paste a key into a command you run.

In CI, export `FAL_KEY` from `fal keys create --scope ADMIN`: `fal deploy` and `fal run`
need an ADMIN-scoped key; an API-scoped key can call endpoints but not deploy or manage apps.

The runner uses the Python minor version of the interpreter you run `fal` from (the app
is cloudpickled); 3.11 is a safe default. To pin one, see `python_version` in
`references/app-configuration.md`, and deploy from a matching interpreter.

## The mental model: what runs where

- **Module top level and the class body run on your machine** during `fal run` /
  `fal deploy`. Anything they reference is pickled and shipped.
- **`setup()`, endpoint methods and `teardown()` run on the remote runner**, inside the
  environment built from `requirements` (or your container image).
- So: import heavy or remote-only packages (`torch`, `diffusers`) **inside** `setup()` or
  the handler, never at module top level. Keep top-level objects small and picklable.
  Never read secrets at top level.
- `setup()` runs once per runner, before it takes requests. Load models there and keep
  them on `self`.

## Minimal complete app

```python
# app.py
import fal
from fal.toolkit import Image
from pydantic import BaseModel, Field


class Input(BaseModel):
    prompt: str = Field(description="Text prompt", examples=["a red fox in snow"])
    steps: int = Field(default=4, ge=1, le=50)
    seed: int | None = None


class Output(BaseModel):
    image: Image
    seed: int


class TextToImage(fal.App):
    app_name = "text-to-image"             # endpoint: <owner>/text-to-image
    machine_type = "GPU-H100"
    requirements = [
        "torch==2.5.1",
        "diffusers==0.31.0",
        "transformers==4.46.3",
        "accelerate==1.1.1",
    ]
    keep_alive = 300                       # seconds an idle runner stays warm
    max_concurrency = 4
    startup_timeout = 900                  # first boot downloads weights

    def setup(self):
        import torch
        from diffusers import AutoPipelineForText2Image

        # HF_HOME is preset to /data/.cache/huggingface, so weights are cached across runners.
        self.pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16"
        ).to("cuda")
        self.pipe("warmup", num_inference_steps=1)   # compile lazy kernels once

    @fal.endpoint("/")
    def generate(self, input: Input) -> Output:
        import random
        import torch

        seed = input.seed if input.seed is not None else random.randint(0, 2**31 - 1)
        generator = torch.Generator("cuda").manual_seed(seed)
        result = self.pipe(
            input.prompt, num_inference_steps=input.steps,
            guidance_scale=0.0, generator=generator,
        )
        return Output(image=Image.from_pil(result.images[0]), seed=seed)
```

## Workflow

1. **Test on real hardware first:**

   ```bash
   fal run app.py::TextToImage --auth private > fal-run.log 2>&1 &   # never in the foreground
   # poll fal-run.log for "Application startup complete" and the Sync URL, then:
   curl -X POST "$SYNC_URL" -H "Authorization: Key $FAL_KEY" \
     -H 'Content-Type: application/json' -d '{"prompt": "a red fox"}'
   ```

   A private `fal run` URL needs a key from the same account. If you authenticated with
   `fal auth login`, `FAL_KEY` is unset: ask the user to export a key they created with
   `fal keys create` (never create one inline and echo it), or call it from Python with
   `fal.apps.run("<path after https://fal.run/ in the Sync URL>", {"prompt": "a red fox"})`,
   which uses the CLI login and the team chosen with `fal account set`. `fal_client` also
   falls back to the login session when no key is set, but ignores the selected team.

   `fal run` runs until stopped and bills the runner meanwhile: kill its pid as soon as
   you are done (or pass `--limit-max-requests 1`). It is ephemeral, ignores `app_auth`
   and pyproject `auth`, and without `--auth private` is **public**, callable by anyone
   with the URL on your bill. Skipping this step is the usual reason a first deploy
   crash-loops. `fal run --local app.py::TextToImage` serves on `http://localhost:8080`
   using your local packages and hardware instead.

2. **Deploy (confirm with the user first):**

   ```bash
   fal apps list --filter text-to-image            # does an app with this name exist?
   fal deploy app.py::TextToImage                 # private auth, rolling strategy
   fal deploy app.py::TextToImage --env staging   # separate app in another environment
   fal deploy app.py::TextToImage --message "$(git rev-parse --short HEAD)"
   ```

   Before deploying, tell the user the app name, environment, machine type and any
   non-zero `min_concurrency` (billed around the clock), and ask before deploying over
   an existing app with the same name. If the deploy prints a pre-deploy summary and
   exits asking for confirmation (from `--check`, `FAL_DEPLOY_CHECK` or a team policy),
   show that summary to the user and add `--yes` only after they approve.

   The output lists the Playground and the `Sync` / `Async` URLs. A rolling deploy
   switches traffic only once a new runner's `setup()` succeeds, so it blocks until then.

3. **Call it** (see `references/calling-and-testing.md`):

   ```python
   import fal_client
   result = fal_client.subscribe("my-org/text-to-image", arguments={"prompt": "a red fox"})
   print(result["image"]["url"])
   ```

   Or `fal api my-org/text-to-image prompt="a red fox"`. REST (sync `fal.run` and queue
   `queue.fal.run`) is in the reference.

## Most-used App attributes

| Attribute | Default | Notes |
|---|---|---|
| `machine_type` | `"S"` | `XS` `S` `M` `L` `XL` (CPU), `GPU-A100` `GPU-L40` `GPU-H100` `GPU-RTXPRO6000` `GPU-H200` `GPU-B200`. A list is a fallback order. |
| `num_gpus` | unset (server default) | GPUs per runner, for multi-GPU; only applies to GPU machine types. |
| `requirements` | `[]` | Pin versions. `--extra-index-url`, `<url>` pairs go before the packages that need them. |
| `app_name` / `app_auth` | kebab-case class name / `private` on deploy | `public`, `private` or `shared`. `shared` (callers pay with their own key) must first be enabled on the account by fal. |
| `keep_alive` | 60 | Idle seconds before a runner shuts down. |
| `min_concurrency` / `max_concurrency` | 0 / unset (server default 2) | Always-warm floor (billed 24/7) and runner ceiling. Set `max_concurrency` explicitly. |
| `concurrency_buffer` | 0 | Warm runners above current demand. |
| `max_multiplexing` | 1 | Concurrent requests per runner; only with async or thread-safe handlers. |
| `startup_timeout` / `request_timeout` | 600 / 3600 | Seconds for `setup()` / per request. |
| `regions` | any | `us-west` `us-central` `us-east` `eu-north` `eu-west`. |
| `secrets` | account default | Allowlist of secret names exposed as env vars. |
| `image` | none | `ContainerImage` for a custom Dockerfile. |
| `app_files` / `local_python_modules` | `[]` | Ship local files/modules (fal Runtime only). |
| `termination_grace_period_seconds` | 5 | SIGTERM-to-SIGKILL budget for draining and `teardown()`. |

Full table, retry settings and pyproject keys: `references/app-configuration.md`.

Scaling values in code apply on the **first** deploy. Later deploys keep whatever is
live (including `fal apps scale` changes) unless you pass `--reset-scale`. With a
pyproject name reference (`fal deploy text-to-image`) the CLI `--reset-scale` and
`--strategy` flags are silently ignored: set `app_scale_settings = true` /
`deployment_strategy` in `[tool.fal.apps.<name>]`, or deploy by file reference.

## Endpoints

- `@fal.endpoint("/")` for the main route. Add more with other paths
  (`@fal.endpoint("/enhance")` becomes `<owner>/<app>/enhance`).
- One Pydantic model parameter is the JSON body and the return annotation is the output
  schema. Both drive the OpenAPI spec and the dashboard Playground.
- Handlers can be sync or `async`.
- Streaming `@fal.endpoint("/stream")` (SSE `StreamingResponse`); WebSockets
  `@fal.realtime("/realtime")`; health `@fal.endpoint("/health", health_check=fal.HealthCheck(...))`.
- Return errors with `fastapi.responses.JSONResponse(status_code=422, content={"detail": ...})`.
  **Never return 503 for ordinary errors**: a 503 stops the runner.

Details: `references/streaming-realtime-health.md`.

## Files and storage

- **Outputs:** wrap generated media in `fal.toolkit.Image.from_pil(...)`,
  `Image.from_bytes(data, format="png")`, `Video.from_path(...)`, `Audio.from_path(...)`,
  or `File.from_path(...)` / `File.from_bytes(...)`. These upload to the fal CDN and
  return `url`, `content_type`, `file_name`, `file_size`. Never return a raw PIL image.
- **Inputs:** accept URLs (`image_url: str`) and fetch them with
  `fal.toolkit.download_file(url, target_dir=d)` into a per-request directory
  (`with tempfile.TemporaryDirectory() as d:`), or type the field as `Image` and call
  `.to_pil()`. A shared `target_dir` can hand one request another request's file.
- **`/data`:** a persistent volume shared by every runner and app in the account. Put
  weights and caches there, never in the image. HuggingFace downloads land there
  automatically.
- `/tmp` is per-runner scratch space, shared by every request on that runner.

Details: `references/inputs-outputs-files.md`.

## Secrets

Ask the user to set secret values themselves, in the dashboard or in their own terminal:

```bash
fal secrets set HF_TOKEN=<value>           # the user runs this; add --env staging for another environment
fal secrets list                           # names only; safe for you to run
```

Never type a real secret value into a command you run: it lands in shell history and
the transcript.

```python
import os

import fal

class MyApp(fal.App):
    secrets = ["HF_TOKEN"]                  # optional allowlist
    def setup(self):
        token = os.environ["HF_TOKEN"]      # read at runtime, not at import time
```

Secrets are injected when a runner starts. After changing one, restart runners with
`fal apps rollout <app>` (ask the user first on a live app). At build time use `${HF_TOKEN}` inside `requirements` entries or
`ContainerImage(secrets=...)`; there are no secret env vars during the build.

## Custom containers (short version)

```python
from importlib.metadata import version

import fal
from fal.container import ContainerImage

class MyApp(fal.App):
    machine_type = "GPU-A100"
    image = ContainerImage.from_dockerfile_str(f"""
FROM pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime
RUN apt-get update && apt-get install -y curl ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir diffusers==0.31.0 transformers==4.46.3
RUN pip install --no-cache-dir fal=={version("fal")}
""")
```

The image must have `curl`, and installing `fal` last keeps `pydantic`, `protobuf` and
`boto3` compatible. Pin every package; the f-string pins `fal` to the version you
deploy with (the class body runs on your machine). A dev or source install reports a
version that is not on PyPI (e.g. `1.81.2.dev0+d20260928`) and the build fails: pin a
released version literally instead. `app_files` is not allowed with
`image`; use `COPY`. To deploy an existing HTTP server unchanged, use `exposed_port` in
`pyproject.toml` (Direct Server Mode). See `references/containers.md`.

## pyproject.toml

```toml
[tool.fal.apps.text-to-image]
ref = "app.py::TextToImage"
auth = "private"
python_version = "3.11"
```

Then `fal run text-to-image --auth private` and `fal deploy text-to-image`. With a name
reference, `fal deploy` rejects `--app-name`/`--auth` and reads `deployment_strategy`
and `app_scale_settings` from the file. For `ref` apps, the table's `name` (default: the
table key) and `auth` replace the class `app_name`/`app_auth`; for every other setting a
value set on the class wins over the table, and a table `requirements` is ignored. Keep
each setting in one place.

## Environments

`fal environments create staging`, then pass `--env staging` to `deploy`, `run`,
`secrets` and `apps`. Each environment is a separate app (`my-org/my-app--staging`)
with its own secrets; nothing falls back to `main`.

## Pitfalls checklist

- Heavy imports at module top level fail locally or bloat the pickle. Move them into methods.
- Do not define `__init__` on the App (it raises); use `setup()`.
- Local and remote Python minor versions must match; the SDK refuses a mismatch.
- Editing scaling values in code does nothing on a redeploy without `--reset-scale`
  (see above). `machine_type`, `max_multiplexing` and `startup_timeout` always come from code.
- A slow first `setup()` (weight download) can exceed `startup_timeout` (600 s by
  default) and crash-loop. Raise it, or pre-stage weights on `/data`.
- `max_multiplexing > 1` with a synchronous, non-thread-safe handler corrupts state.
- Pin `requirements`. Unpinned `torch` can resolve to a build that does not match the GPU's CUDA.
- There is no `fal.toolkit.upload_image`. Use `Image.from_pil(...)`.
- `FAL_KEY` inside a runner belongs to the app owner. Chained `fal_client` calls are billed to the owner.

## References

- `references/app-configuration.md`: read when you need an attribute not listed above,
  retries, lifecycle hooks, or the full `pyproject.toml` schema.
- `references/inputs-outputs-files.md`: read when handling media inputs or outputs,
  `/data`, the KV store, request headers or runtime env vars.
- `references/containers.md`: read when you need a Dockerfile, private registry,
  build secrets or Direct Server Mode.
- `references/streaming-realtime-health.md`: read when adding SSE, WebSockets, health
  checks, cancellation, graceful shutdown or custom status codes.
- `references/calling-and-testing.md`: read when calling the app (Python, JS, REST,
  webhooks) or writing automated tests.

Public docs: https://fal.ai/docs/documentation/development/app-lifecycle and https://fal.ai/docs/documentation/deployment/deploy-to-production
