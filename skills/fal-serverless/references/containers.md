# Custom container images

Use a container when you need system packages (`ffmpeg`, `libgl1`), a specific CUDA or
base image, non-Python dependencies, or an existing Docker image. Otherwise prefer plain
`requirements`: it is simpler and fal handles CUDA for the chosen machine type.

Builds run remotely (no local Docker needed). Images are cached by a hash of the
Dockerfile, build args, build secrets and the content of every file the Dockerfile
`COPY`s/`ADD`s. With a file-reference app (`app.py::MyApp`) the app file itself is
pickled at deploy time and is not part of the image, so editing it does not rebuild.

## Inline Dockerfile

```python
from importlib.metadata import version

import fal
from fal.container import ContainerImage
from fal.toolkit import Image
from pydantic import BaseModel

# Pin every package. The f-string pins fal to the version you deploy with. A dev or
# source install (e.g. 1.81.2.dev0+d20260928) is not on PyPI, so pip fails the build:
# write a released version literally instead.
DOCKERFILE = f"""
FROM pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime
RUN apt-get update && apt-get install -y --no-install-recommends curl ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir diffusers==0.31.0 transformers==4.46.3 accelerate==1.1.1
# Install fal last so pydantic/protobuf/boto3 match the fal runtime.
RUN pip install --no-cache-dir fal=={version("fal")}
"""

class Input(BaseModel):
    prompt: str

class Output(BaseModel):
    image: Image

class MyApp(fal.App):
    machine_type = "GPU-A100"
    image = ContainerImage.from_dockerfile_str(DOCKERFILE)

    def setup(self):
        import torch
        from diffusers import AutoPipelineForText2Image
        self.pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16
        ).to("cuda")

    @fal.endpoint("/")
    def generate(self, input: Input) -> Output:
        return Output(image=Image.from_pil(self.pipe(input.prompt).images[0]))
```

Platform requirements for a container that runs a `fal.App`:

1. `curl` must be installed (used during runner startup).
2. `pydantic`, `protobuf` and `boto3` must be compatible with the fal SDK. Installing
   `fal` as the last step is the easiest way to guarantee it.

Also from a file: `ContainerImage.from_dockerfile("docker/Dockerfile", context_dir="./my-project")`.

Rules:

- Enforced by the SDK: `app_files` cannot be combined with `image` (raises `app_files is not supported for container apps.`). Use `COPY` instead.
- Per the docs, local-path `requirements` and `local_python_modules` are supported only on the fal Runtime. The SDK does not reject them for container apps, so do not rely on them there; install your code in the Dockerfile.

## ContainerImage parameters

Passed as keyword arguments to `from_dockerfile_str()` / `from_dockerfile()`:

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `build_args` | `dict[str, str]` | `{}` | `--build-arg` values. Visible in image layers; never put secrets here. |
| `secrets` | `dict[str, str]` | `{}` | BuildKit secret mounts (`RUN --mount=type=secret,id=<key> ...`, read from `/run/secrets/<key>`). A value of `"$NAME"` or `"${NAME}"` resolves from your fal secret `NAME`. Not persisted in the image. |
| `registries` | `dict[str, dict]` | `{}` | Private registry creds: `{"<registry-host>": {"username": ..., "password": ...}}`. Both keys are required. `"$NAME"` in the password references a fal secret; write `$$` for a literal `$`. |
| `context_dir` | path | current working directory | Build context for `COPY`/`ADD`. |
| `dockerignore` | `list[str]` | `dockerignore_path` if given, else `<context_dir>/.dockerignore` if present, else built-in defaults (`.git`, `.env`, `.venv`, `*.md`, `Dockerfile`, `node_modules`, ...) | Patterns excluded from the context. An explicit list, `dockerignore_path` or a `.dockerignore` in the context replaces the defaults entirely, so repeat `.env`, `.git` and `.venv` in it or a `COPY . .` ships them (and any secrets in `.env`) into the image. |
| `dockerignore_path` | path | `None` | Path to a `.dockerignore` file. |
| `compression` | `str` | `"gzip"` | Layer compression (`"gzip"` or `"zstd"`). |
| `force_compression` | `bool` | `False` | Re-compress all layers. |
| `entrypoint` / `cmd` | `str` or `list[str]` | `None` | ENTRYPOINT / CMD overrides. |

`builder="service"` / `"worker"` are deprecated; all builds use Depot. Omit `builder`.

`COPY`/`ADD` of local files is marked experimental in the docs. Paths resolve relative
to `context_dir`, which defaults to where you run `fal deploy`, so run it from the
project root or set `context_dir=Path(__file__).parent`.

## Build secrets and private packages

```python
from importlib.metadata import version  # pin fal as in the first example

image = ContainerImage.from_dockerfile_str(
    f"""
    FROM python:3.11
    RUN apt-get update && apt-get install -y curl
    RUN --mount=type=secret,id=pip_token pip install --no-cache-dir \
        --extra-index-url https://$(cat /run/secrets/pip_token)@pypi.example.com/simple \
        my-private-package
    RUN pip install --no-cache-dir fal=={version("fal")}
    """,
    secrets={"pip_token": "${MY_PIP_TOKEN}"},
)
```

Secrets are never exposed as environment variables during the build. Use the `${NAME}`
reference (resolved from the secret stored on fal) instead of `os.getenv(...)`, which
reads the deploying machine's environment and silently becomes `None` in CI. An unknown
name is not an error: the literal placeholder is passed through and the install fails
with an auth error, so check names against `fal secrets list`.

For the fal Runtime (no container), the same substitution works inside `requirements`:
`requirements = ["git+https://${GITHUB_TOKEN}@github.com/my-org/private-package"]`.

## Private base images

```python
from importlib.metadata import version  # pin fal as in the first example

class MyApp(fal.App):
    image = ContainerImage.from_dockerfile_str(
        f"""
        FROM my-org/private-base:1.2.0
        RUN apt-get update && apt-get install -y --no-install-recommends curl \\
            && rm -rf /var/lib/apt/lists/*
        RUN pip install --no-cache-dir fal=={version("fal")}
        """,
        registries={
            "https://index.docker.io/v1/": {
                "username": "my-user",
                "password": "$DOCKERHUB_TOKEN",   # a fal secret, never the token itself
            },
        },
    )
```

The base image still needs `curl` and `fal` (installed last), as for any container.
Ask the user to store the registry token as a fal secret in the dashboard or with
`fal secrets set` in their own terminal; never type the token into a command you run or
into the code.

Google Artifact Registry: username `_json_key_base64`, password = a fal secret holding the
base64 service-account JSON. AWS ECR: username `AWS`, password from
`aws ecr get-login-password` (expires after 12 hours; refresh the secret). Guide:
https://fal.ai/docs/documentation/development/private-registries

## pyproject.toml image config and existing servers

`[tool.fal.apps.<name>.image]` takes either `dockerfile = "Dockerfile"` (with optional
`build_args`, `secrets`, `registries`, `entrypoint`, `cmd`) or `image = "my-org/app:tag"`
(with optional `registries`, `entrypoint`, `cmd`; `build_args`/`secrets` are rejected).
If the app has neither `ref` nor `python_entry_point`, fal runs the container as-is
without the fal Python loader. Combine that with `exposed_port` to deploy an existing
HTTP server (Direct Server Mode):

```toml
[tool.fal.apps.my-server]
auth = "private"
machine_type = "GPU-A100"
exposed_port = 8000

[tool.fal.apps.my-server.image]
dockerfile = "Dockerfile"
```

```bash
fal deploy my-server
```

The server must listen on `0.0.0.0` at the exposed port. The scaling keys
(`keep_alive`, `min_concurrency`, `max_concurrency`, ...) work the same way. Walkthrough:
https://fal.ai/docs/documentation/development/migrate-external-docker-server

## Image size and cold starts

Image size drives cold-start time whenever a runner lands on a node that does not have
the image cached. The scheduler prefers nodes that already hold it, and after a rebuild
only changed layers are re-pulled. Use
`-runtime` rather than `-devel` CUDA bases when you do not compile, clean apt lists,
use `pip install --no-cache-dir`, and keep model weights out of the image (put them on
`/data` or download in `setup()`).
https://fal.ai/docs/documentation/serverless/optimizations/optimize-container-images
