---
name: fal-serverless
description: Build, test and deploy your own Python apps on fal Serverless GPUs with the `fal` SDK and CLI. Covers writing a `fal.App` (setup(), `@fal.endpoint`, Pydantic input/output, requirements, machine_type, scaling, secrets, fal.toolkit file outputs, /data storage, custom container images, pyproject `[tool.fal.apps]`), testing with `fal run`, shipping with `fal deploy`, and calling the endpoint. Use when the user says "deploy to fal", "fal.App", "fal run", "fal deploy", "serverless GPU app on fal", "host my model on fal", "fal.endpoint", "machine_type", or edits code that imports `fal`. This skill is for building and hosting your own apps with the `fal` CLI. It is not for calling existing fal marketplace models (that is the genmedia CLI). For debugging, scaling or operating an app that is already deployed, use fal-serverless-operate.
---

# fal Serverless: build and deploy a fal.App

You write a Python class that subclasses `fal.App`. `fal run` boots it on a temporary
cloud runner for testing, and `fal deploy` makes it a persistent, autoscaling HTTP/queue
endpoint at `<owner>/<app-name>`. Builds happen remotely, so no local Docker or GPU is
needed.

This file covers what you need to get an app running. For anything else, check
`fal <command> --help` (it always matches the installed version) and the docs linked at
the end, rather than guessing.

## Setup

```bash
pip install fal            # the SDK + CLI (also install it in the project's venv)
fal auth whoami            # which account is in use
```

If `whoami` fails, ask the user to authenticate. The simplest path from an agent shell
is for the user to export `FAL_KEY` themselves, or to run `fal auth login` in their own
terminal. If you run it yourself, it blocks until the browser step completes and then
asks for an account, so run it in the background with that answer piped in, and read the
URL from the log:

```bash
printf '\n' | fal auth login --connection github --no-browser > fal-login.log 2>&1 &
# (or google, or their SSO domain); the empty line picks the default account
```

Give the user the URL from `fal-login.log`, wait for the job to exit, then re-check
`fal auth whoami`. Never paste a key into a command you run.

In CI, the user exports `FAL_KEY` from a key made with
`fal keys create --preset SERVERLESS` (build, deploy and run apps). An `--preset API` key
can only call endpoints. Do not suggest `--scope ADMIN`: it is deprecated and makes a key
with full access to the account, billing included.

The runner uses the Python minor version of the interpreter you run `fal` from (the app
is cloudpickled), and the SDK refuses a mismatch. Deploy from the version you mean to run.

## The mental model: what runs where

- **Module top level and the class body run on your machine** during `fal run` /
  `fal deploy`. Anything they reference is pickled and shipped.
- **`setup()`, endpoint methods and `teardown()` run on the remote runner**, inside the
  environment built from `requirements` (or your container image).
- So: import heavy or remote-only packages (`torch`, `diffusers`) **inside** `setup()` or
  the handler, never at module top level. Keep top-level objects small and picklable.
  Never read secrets at top level.
- `setup()` runs once per runner, before it takes requests. Load models there and keep
  them on `self`. Never define `__init__` on the App; it raises.

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
   `fal auth login`, `FAL_KEY` is unset: ask the user to export a key they created, or
   call it from Python with
   `fal.apps.run("<path after https://fal.run/ in the Sync URL>", {"prompt": "a red fox"})`,
   which uses the CLI login.

   `fal run` bills the runner until stopped: kill its pid as soon as you are done (or pass
   `--limit-max-requests 1`). Without `--auth private` it is **public**, callable by
   anyone with the URL on your bill. Skipping this step is the usual reason a first
   deploy crash-loops.

2. **Deploy (confirm with the user first):**

   ```bash
   fal apps list --filter text-to-image            # does an app with this name exist?
   fal deploy app.py::TextToImage                 # private auth, rolling strategy
   fal deploy app.py::TextToImage --env staging   # separate app in another environment
   ```

   Before deploying, tell the user the app name, environment, machine type and any
   non-zero `min_concurrency` or `concurrency_buffer` (both keep runners up, and billed,
   around the clock), and ask before deploying over an existing app with the same name.
   If the deploy prints a summary and exits asking for confirmation, show that summary
   to the user and add `--yes` only after they approve.

3. **Call it:**

   ```python
   import fal_client
   result = fal_client.subscribe("my-org/text-to-image", arguments={"prompt": "a red fox"})
   print(result["image"]["url"])
   ```

   Or `fal api my-org/text-to-image prompt="a red fox"`. For REST, the queue, webhooks
   and JavaScript, see the calling docs below.

## App attributes

| Attribute | Notes |
|---|---|
| `machine_type` | CPU (`S` is the default) or GPU such as `GPU-A100`, `GPU-H100`. A list is a fallback order. Names: machine types docs. |
| `requirements` | Pin every version. Unpinned `torch` can resolve to a build that does not match the GPU's CUDA. |
| `app_name` / `app_auth` | Every deploy applies `app_auth` from code (default `private`), so a redeploy without it makes a public app private. |
| `keep_alive` | Idle seconds before a runner shuts down. |
| `min_concurrency` / `concurrency_buffer` | Runners kept up even at zero traffic: billed 24/7. |
| `max_concurrency` | Runner ceiling. Set it explicitly. |
| `max_multiplexing` | Concurrent requests per runner; only with async or thread-safe handlers. |
| `startup_timeout` / `request_timeout` | Seconds for `setup()` / per request. A slow first `setup()` (weight download) can exceed `startup_timeout` and crash-loop. |
| `secrets` | Allowlist of secret names; see Secrets. |
| `image` | `ContainerImage` for a custom image; see Custom containers. |

Scaling values, `request_timeout` and `regions` in code apply on the **first** deploy.
Later deploys keep whatever is live (including `fal apps scale` changes) unless you pass
`--reset-scale`. `machine_type`, `max_multiplexing` and `startup_timeout` always come
from code.

## Endpoints

- `@fal.endpoint("/")` for the main route; other paths (`@fal.endpoint("/enhance")`)
  become `<owner>/<app>/enhance`.
- One Pydantic model parameter is the JSON body and the return annotation is the output
  schema. Both drive the OpenAPI spec and the dashboard Playground.
- Handlers can be sync or `async`. Streaming, WebSockets and health checks: docs below.
- Return errors with `fastapi.responses.JSONResponse(status_code=422, content={"detail": ...})`.
  **Never return 503 for ordinary errors**: a 503 stops the runner.

## Files and storage

- **Outputs:** wrap generated media in `fal.toolkit.Image.from_pil(...)`,
  `Image.from_bytes(data, format="png")`, `Video.from_path(...)`, `Audio.from_path(...)`,
  or `File.from_path(...)`. These upload to the fal CDN and return a URL. Never return
  a raw PIL image.
- **Inputs:** accept URLs (`image_url: str`) and fetch them with
  `fal.toolkit.download_file(url, target_dir=d)` into a per-request directory
  (`with tempfile.TemporaryDirectory() as d:`). A shared `target_dir` can hand one
  request another request's file.
- **`/data`:** a persistent volume shared by every runner and app in the account. Put
  weights and caches there, never in the image. Write to a temp name and rename into
  place, so another runner never reads a partial file.
- `/tmp` is per-runner scratch space, shared by every request on that runner.

## Secrets

Ask the user to set secret values themselves, in the dashboard or in their own terminal
(`fal secrets set HF_TOKEN=<value>`). Never type a real value into a command you run.
`fal secrets list` shows names only and is safe to run.

```python
import os

import fal

class MyApp(fal.App):
    secrets = ["HF_TOKEN"]                  # optional allowlist
    def setup(self):
        token = os.environ["HF_TOKEN"]      # read at runtime, not at import time
```

- Without `secrets`, the app gets every secret exposed by default. With it, the app gets
  only the names listed, **at build time too**.
- A secret set with `--not-exposed-by-default` reaches only apps that list it. Setting it
  again without that flag makes it exposed again.
- There are no secret env vars during the build. `${NAME}` is substituted in
  `requirements` entries and in `ContainerImage(secrets={...})` values (for
  `RUN --mount=type=secret` steps); a name the app cannot see stays literal.
- Secrets are injected when a runner starts. After changing one, restart runners with
  `fal apps rollout <app>` (ask the user first on a live app).

## Custom containers

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

- The image must have `python3.X` on `PATH` with the **same minor version** as the
  interpreter you deploy from; otherwise the build fails. Check the base image's Python
  before choosing it.
- Install `curl`, and install `fal` last so `pydantic`, `protobuf` and `boto3` stay
  compatible (a mismatch breaks the runner, not the build). The f-string pins `fal` to the version you deploy with; if that is a dev
  or source install (a version not on PyPI), pin a released version literally.
- `app_files` is not allowed with `image`; use `COPY`.

## Environments and pyproject

- `fal environments create staging`, then pass `--env staging` to `deploy`, `run`,
  `secrets` and `apps`. Each environment is a separate app (`my-org/my-app--staging`)
  with its own secrets; nothing falls back to `main`.
- An app can be declared in `pyproject.toml` under `[tool.fal.apps.<name>]` with
  `ref = "app.py::MyApp"` and deployed by name (`fal deploy <name>`). Keep each setting
  in one place: the class or the table. See the pyproject docs.

## Docs

- Lifecycle and deploying: https://fal.ai/docs/documentation/development/app-lifecycle,
  https://fal.ai/docs/documentation/deployment/deploy-to-production
- Machine types: https://fal.ai/docs/documentation/deployment/machine-types
- Scaling: https://fal.ai/docs/documentation/deployment/scaling-configuration
- Inputs, outputs and files: https://fal.ai/docs/documentation/development/handle-inputs-and-outputs,
  https://fal.ai/docs/documentation/development/use-persistent-storage
- Secrets: https://fal.ai/docs/documentation/development/manage-secrets-securely
- Streaming, realtime, health checks, cancellation:
  https://fal.ai/docs/documentation/development/streaming,
  https://fal.ai/docs/documentation/development/realtime,
  https://fal.ai/docs/documentation/development/add-health-check-endpoint,
  https://fal.ai/docs/documentation/development/handle-cancellations
- Containers: https://fal.ai/docs/documentation/serverless/optimizations/optimize-container-images,
  https://fal.ai/docs/documentation/development/private-registries,
  https://fal.ai/docs/documentation/development/migrate-external-docker-server
- pyproject: https://fal.ai/docs/api-reference/python-sdk/pyproject-toml
- Calling and testing: https://fal.ai/docs/documentation/development/calling-your-endpoints,
  https://fal.ai/docs/documentation/model-apis/inference/queue,
  https://fal.ai/docs/documentation/development/test-models-and-endpoints
