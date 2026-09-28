# Inputs, outputs, files and storage

Endpoint signatures are FastAPI: a single Pydantic model parameter is the JSON body,
the return annotation is the response schema, and both generate the OpenAPI spec the
dashboard Playground renders. You can also accept `request: fastapi.Request` or
`response: fastapi.Response` parameters.

## Schemas

```python
from typing import List, Optional
from fal.toolkit import FalBaseModel, Field, Hidden, ImageField, Image

class Input(FalBaseModel):
    FIELD_ORDERS = ["prompt", "image_url", "num_images"]   # Playground/schema order
    prompt: str = Field(description="What to generate", examples=["a red fox"])
    image_url: Optional[str] = ImageField(default=None, description="Optional init image")
    num_images: int = Field(default=1, ge=1, le=4)
    debug: bool = Hidden(Field(default=False))               # API-only, hidden in UI

class Output(FalBaseModel):
    images: List[Image]
    seed: int
```

- Plain `pydantic.BaseModel` works too; `FalBaseModel` adds `FIELD_ORDERS` and `Hidden`.
- `Hidden(...)` fields must have a default or `default_factory`.
- Playground widgets: `FileField`, `ImageField`, `AudioField`, `VideoField`, or name a
  `str` field with the suffix `file_url`, `image_url`, `audio_url`, `video_url`
  (`image_urls: List[str]` renders a dataset input).
- Output media renders when the object has both `url` and `content_type`. The toolkit
  types set both. Field names the Playground recognises: `image`/`images`, `video`,
  `audio`/`audio_file`/`audio_url`, `model_glb`/`model_obj`/`model_mesh`.

## Reading input files

```python
from fal.toolkit import download_file, Image

@fal.endpoint("/")
def run(self, input: Input) -> Output:
    path = download_file(input.video_url, target_dir="/tmp/inputs")   # returns pathlib.Path
    ...
```

- `download_file(url, target_dir, *, force=False, request_headers=None, filesize_limit=None)`.
  `target_dir` is required. A relative `target_dir` resolves under `/data`. `data:` URIs
  are decoded without a network call. Re-downloading is skipped when a local file with the
  same `Content-Length` exists (size, not hash; pass `force=True` for freshness).
  `filesize_limit` is in MB.
- An `Image`-typed input field accepts a URL string; call `.to_pil()` on it to load it.
- `File.save(path)` downloads a file object to a path. `File.as_bytes()` only works on
  objects created from bytes in this process (`file_data` is set); on an object built
  from a URL it raises `ValueError("File has not been downloaded")`.

## Returning files (upload to the fal CDN)

```python
from fal.toolkit import File, Image, Video, Audio

Image.from_pil(pil_image)                       # png by default; format="jpeg"|"webp"|"gif"|"jpg"
Image.from_bytes(raw, format="png")
Image.from_path("/tmp/out.png")
Video.from_path("/tmp/out.mp4")
Audio.from_path("/tmp/out.wav")
Audio.from_bytes(raw, content_type="audio/wav", file_name="out.wav")
File.from_path("/tmp/result.glb")
File.from_bytes(data, content_type="application/octet-stream", file_name="model.glb")
```

Each call uploads immediately and returns a model with `url`, `content_type`,
`file_name`, `file_size` (plus `width`/`height` for `Image`). Return it inside your
output model. URLs are public by default and expire according to the account's media
expiration settings. There is no `fal.toolkit.upload_image` helper; use the classes above.

Return a raw PIL image or tensor and serialization fails; always wrap it.

`CompressedFile(url=...)` is a `File` for ZIP archives: iterate it or call
`.glob("*.png")` to extract and walk the contents.

## Storage choices

| | fal CDN (toolkit types) | `/data` | `/tmp` |
|---|---|---|---|
| Use for | outputs returned to callers | model weights, datasets, caches | per-request scratch |
| Lifetime | media expiration setting | until deleted | runner lifetime |
| Shared | no (unique URL per upload) | across all runners **and all apps** in the account | no |
| Access | public URL (ACL-restrictable) | filesystem only | filesystem only |

### Persistent `/data`

- Mounted on every runner, eventually consistent across datacenters.
- `HF_HOME` is preset to `/data/.cache/huggingface`, so `transformers` /
  `diffusers` / `huggingface_hub` downloads are cached across runners automatically.
- `fal.toolkit.download_model_weights(url, force=False, request_headers=None)` caches
  a file under `/data/.fal/model_weights/`. `fal.toolkit.clone_repository(url,
  commit_hash=..., include_to_path=True)` clones into `/data/.fal/repos/`.
- Constants: `FAL_PERSISTENT_DIR` (`/data`), `FAL_MODEL_WEIGHTS_DIR`, `FAL_REPOSITORY_DIR`.
- Concurrent writers: write to a temp file in the same directory, then `os.rename` it
  into place so other runners never read a partial file.
- Multi-file models load faster after a parallel pre-read that warms the cache:
  `find /data/models/x -type f | xargs -P 32 -I {} cat {} > /dev/null`.
- Upload from your machine with `fal files upload <local> <remote>` (paths relative to
  `/data`; refuses to overwrite, `fal files rm` first). Or write from a one-off function:

```python
import fal

@fal.function(machine_type="S")
def fetch_weights():
    import urllib.request
    urllib.request.urlretrieve("https://example.com/w.safetensors", "/data/models/w.safetensors")
```

Run it with `fal run fetch.py::fetch_weights`.

### KV store (small shared values)

```python
from fal.toolkit import KVStore

kv = KVStore("my-namespace")
kv.set("key", json.dumps(obj), ttl=3600)   # str values only, <= 1.9 MB, ttl 60..2592000 s
value = kv.get("key")                      # None if missing
kv.delete("key")
```

Default TTL is 30 days. No listing, no atomic ops, last write wins. Do not use it for
counters or locks.

## Secrets and environment at runtime

- `fal secrets set HF_TOKEN=...` then read `os.environ["HF_TOKEN"]` in `setup()` or a
  handler. Never read secrets at module top level: that runs on your machine and the value
  gets pickled into the app.
- Runners see secrets from their own environment only (`--env staging` secrets do not
  fall back to `main`). Updated secrets reach only new runners: run
  `fal apps rollout <app>` after changing one.
- Platform-injected variables: `FAL_KEY` (owner-scoped key; `fal_client` picks it up, and
  calls are billed to you), `FAL_APP_NAME`, `FAL_APP_ID`, `FAL_USER_NICKNAME`,
  `FAL_JOB_ID` (runner id), `FAL_HOST`, `FAL_REGION`, `FAL_RUNNER_STATE`
  (`SETUP`/`RUNNING`/`TERMINATING`), `HF_HOME`. None of these exist during the image build.

## Request context

```python
@fal.endpoint("/")
def run(self, input: Input) -> Output:
    req = self.current_request
    request_id = req.request_id                      # also header x-fal-request-id
    caller = req.headers.get("x-fal-caller-user-id")
    ...
```

Custom caller headers are forwarded (names are case-insensitive; callers cannot set
`x-fal-*`). Total response headers must stay under 16 KB.

Docs:
- https://fal.ai/docs/documentation/development/handle-inputs-and-outputs
- https://fal.ai/docs/documentation/development/working-with-files
- https://fal.ai/docs/documentation/development/use-persistent-storage
- https://fal.ai/docs/documentation/development/manage-secrets-securely
