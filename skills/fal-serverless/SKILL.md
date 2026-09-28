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
fal auth login             # browser login; or export FAL_KEY=<key_id>:<key_secret>
fal auth whoami
```

In CI, export `FAL_KEY` from `fal keys create --scope ADMIN`: `fal deploy` and `fal run`
need an ADMIN-scoped key; an API-scoped key can call endpoints but not deploy or manage apps.

The runner uses the same Python minor version as the interpreter you run `fal` from
(the app is cloudpickled). Pick that interpreter deliberately; 3.11 is a safe default.
To pin a version instead, pass `python_version` as a class keyword or set it in
`pyproject.toml` (see `references/app-configuration.md`) and deploy from a matching
interpreter.

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
   fal run app.py::TextToImage
   ```

   Wait for `Application startup complete`, then call the printed Sync URL:

   ```bash
   curl -X POST "$SYNC_URL" -H 'Content-Type: application/json' -d '{"prompt": "a red fox"}'
   ```

   `fal run` is ephemeral (deleted on Ctrl-C) and **public by default**: anyone with
   the URL can call it. Pass `--auth private` if that matters. It ignores `app_auth`.
   Skipping this step is the usual reason a first deploy crash-loops.
   `fal run --local app.py::TextToImage` serves on `http://localhost:8080` using your
   local packages and hardware instead.

2. **Deploy:**

   ```bash
   fal deploy app.py::TextToImage                 # private auth, rolling strategy
   fal deploy app.py::TextToImage --env staging   # separate app in another environment
   fal deploy app.py::TextToImage --message "$(git rev-parse --short HEAD)"
   ```

   The output lists the Playground, the app overview and the `Sync` / `Async` URLs for
   each endpoint. A rolling deploy starts one runner on the new revision and only
   switches traffic once `setup()` succeeds, so the command blocks until then.

3. **Call it** (see `references/calling-and-testing.md`):

   ```python
   import fal_client
   result = fal_client.subscribe("my-org/text-to-image", arguments={"prompt": "a red fox"})
   print(result["image"]["url"])
   ```

   ```bash
   # Queue submit: returns request_id / status_url / response_url, not the output.
   # Use https://fal.run/my-org/text-to-image to block for the result (no queue retries).
   curl -X POST https://queue.fal.run/my-org/text-to-image \
     -H "Authorization: Key $FAL_KEY" -H "Content-Type: application/json" \
     -d '{"prompt": "a red fox"}'
   ```

   Or from the CLI: `fal api my-org/text-to-image prompt="a red fox"`.

## Most-used App attributes

| Attribute | Default | Notes |
|---|---|---|
| `machine_type` | `"S"` | `XS` `S` `M` `L` `XL` (CPU), `GPU-A100` `GPU-L40` `GPU-H100` `GPU-RTXPRO6000` `GPU-H200` `GPU-B200`. A list is a fallback order. |
| `num_gpus` | unset (server default) | GPUs per runner, for multi-GPU; only applies to GPU machine types. |
| `requirements` | `[]` | Pin versions. `--extra-index-url`, `<url>` pairs go before the packages that need them. |
| `app_name` / `app_auth` | kebab-case class name / `private` on deploy | `public`, `private` or `shared`. |
| `keep_alive` | 60 | Idle seconds before a runner shuts down. |
| `min_concurrency` / `max_concurrency` | 0 / unset (server default 2) | Always-warm floor (billed 24/7) and runner ceiling. Set `max_concurrency` explicitly. |
| `concurrency_buffer` | 0 | Warm runners above current demand. |
| `max_multiplexing` | 1 | Concurrent requests per runner; only with async or thread-safe handlers. |
| `startup_timeout` / `request_timeout` | 600 / platform default | Seconds for `setup()` / per request. |
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
- Streaming: `@fal.endpoint("/stream")` returning an SSE `StreamingResponse`.
- WebSockets: `@fal.realtime("/realtime")` or `@fal.endpoint("/ws", is_websocket=True)`.
- Health check: `@fal.endpoint("/health", health_check=fal.HealthCheck(...))`.
- Return errors with `fastapi.responses.JSONResponse(status_code=422, content={"detail": ...})`.
  **Never return 503 for ordinary errors**: a 503 stops the runner.

Details: `references/streaming-realtime-health.md`.

## Files and storage

- **Outputs:** wrap generated media in `fal.toolkit.Image.from_pil(...)`,
  `Image.from_bytes(data, format="png")`, `Video.from_path(...)`, `Audio.from_path(...)`,
  or `File.from_path(...)` / `File.from_bytes(...)`. These upload to the fal CDN and
  return `url`, `content_type`, `file_name`, `file_size`. Never return a raw PIL image.
- **Inputs:** accept URLs (`image_url: str`) and fetch them with
  `fal.toolkit.download_file(url, target_dir="/tmp/in")`, or type the field as `Image`
  and call `.to_pil()`.
- **`/data`:** a persistent volume shared by every runner and app in the account. Put
  weights and caches there, never in the image. HuggingFace downloads land there
  automatically.
- `/tmp` is per-runner scratch space.

Details: `references/inputs-outputs-files.md`.

## Secrets

```bash
fal secrets set HF_TOKEN=hf_xxx            # add --env staging for another environment
```

```python
import os

class MyApp(fal.App):
    secrets = ["HF_TOKEN"]                  # optional allowlist
    def setup(self):
        token = os.environ["HF_TOKEN"]      # read at runtime, not at import time
```

Secrets are injected when a runner starts. After changing one, run
`fal apps rollout <app>`. At build time use `${HF_TOKEN}` inside `requirements` entries or
`ContainerImage(secrets=...)`; there are no secret env vars during the build.

## Custom containers (short version)

```python
from fal.container import ContainerImage

class MyApp(fal.App):
    machine_type = "GPU-A100"
    image = ContainerImage.from_dockerfile_str("""
FROM pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime
RUN apt-get update && apt-get install -y curl ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir diffusers transformers
RUN pip install --no-cache-dir fal
""")
```

The image must have `curl`, and installing `fal` last keeps `pydantic`, `protobuf` and
`boto3` compatible. `app_files` is not allowed with `image`; use `COPY`. To deploy an
existing HTTP server unchanged, use `exposed_port` in `pyproject.toml` (Direct Server
Mode). See `references/containers.md`.

## pyproject.toml

```toml
[tool.fal.apps.text-to-image]
ref = "app.py::TextToImage"
auth = "private"
python_version = "3.11"
```

After that, use `fal run text-to-image` and `fal deploy text-to-image`. With a name
reference, `fal deploy` rejects `--app-name`/`--auth` and reads the strategy and
reset-scale settings from the file (`deployment_strategy`, `app_scale_settings`).

## Environments

`fal environments create staging`, then pass `--env staging` to `deploy`, `run`,
`secrets` and `apps`. Each environment holds a separate app with its own secrets. The
endpoint id gets a suffix, as in `my-org/my-app--staging`. Secrets do not fall back to
`main`.

## Pitfalls checklist

- Heavy imports at module top level fail locally or bloat the pickle. Move them into methods.
- Do not define `__init__` on the App (it raises); use `setup()`.
- `fal run` URLs are public unless you pass `--auth private`.
- Local and remote Python minor versions must match; the SDK refuses a mismatch.
- Editing scaling values in code does nothing on a redeploy without `--reset-scale`
  (or `app_scale_settings = true` in pyproject.toml when deploying by app name, where
  the CLI flag is ignored).
  `machine_type`, `max_multiplexing` and `startup_timeout` always come from code.
- A slow first `setup()` (weight download) can exceed `startup_timeout` (600 s by
  default) and crash-loop. Raise it, or pre-stage weights on `/data`.
- `max_multiplexing > 1` with a synchronous, non-thread-safe handler corrupts state.
- Changing a secret does not reach running runners. Run `fal apps rollout`.
- Pin `requirements`. Unpinned `torch` can resolve to a build that does not match the GPU's CUDA.
- There is no `fal.toolkit.upload_image`. Use `Image.from_pil(...)`.
- In Dockerfiles, missing `curl` or pip overriding `pydantic`/`protobuf` breaks the fal runtime.
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
