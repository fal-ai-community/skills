# Calling and testing your app

The endpoint id of a deployed app is `<owner>/<app-name>`, plus `--<env>` for non-main
environments (`my-org/my-app--staging`), plus a sub-path for non-root endpoints
(`my-org/my-app/enhance`). The owner is your username or team. `fal deploy` prints the
exact sync and async URLs.

Auth: callers send `Authorization: Key <FAL_KEY>`. Create a key with
`fal keys create --scope API` (API scope is enough to call apps; deploying needs ADMIN). Private apps accept keys from the owning account/team
only.

## Python (`pip install fal-client`)

```python
import fal_client

# Queue + wait (retries, durable). Most common.
result = fal_client.subscribe(
    "my-org/my-app",
    arguments={"prompt": "a red fox"},
    with_logs=True,
    on_queue_update=lambda u: print(u),
)

# Non-root endpoint: either form works
fal_client.subscribe("my-org/my-app/enhance", arguments={"image_url": "https://example.com/in.png"})
fal_client.subscribe("my-org/my-app", arguments={"image_url": "https://example.com/in.png"}, path="/enhance")

# Fire and poll later
handle = fal_client.submit("my-org/my-app", arguments={"prompt": "a red fox"})
print(handle.request_id, handle.status())
result = handle.get()          # blocks until done
# or, instead of get(): handle.cancel()

# Direct call: no queue, no platform retries, no status (fal_client itself still
# retries transport errors, timeouts and 408/409/429, up to 10 attempts)
result = fal_client.run("my-org/my-app", arguments={"prompt": "a red fox"})

# SSE stream (app must define @fal.endpoint("/stream"))
for event in fal_client.stream("my-org/my-app", arguments={"prompt": "a red fox"}):
    print(event)

# Realtime (app must define @fal.realtime("/realtime"))
with fal_client.realtime("my-org/my-app") as conn:
    conn.send({"prompt": "hi"})
    print(conn.recv())

# Upload a local file and pass its URL as input
url = fal_client.upload_file("input.png")
```

Useful keyword arguments on `subscribe`/`submit`: `headers={...}`, `start_timeout=`
(server-side deadline before processing starts; sent as `X-Fal-Request-Timeout`),
`priority="low"`, `hint=` (runner affinity), `webhook_url=` (`submit` only), and
`client_timeout=` (`subscribe` only): total client-side wait. If `start_timeout` is
unset it also becomes the server-side start deadline, and the request is cancelled when
it expires.

Per-request headers: `x-fal-no-retry: 1` disables queue retries;
`X-Fal-Retry-Config: {"server_error": {"retries": 3}}` (JSON) overrides retry budgets on
your own apps.

## JavaScript (`npm install @fal-ai/client`)

```javascript
import { fal } from "@fal-ai/client";
const result = await fal.subscribe("my-org/my-app", { input: { prompt: "a red fox" } });
console.log(result.data);
```

## REST

```bash
# Synchronous
curl -X POST https://fal.run/my-org/my-app \
  -H "Authorization: Key $FAL_KEY" -H "Content-Type: application/json" \
  -d '{"prompt": "a red fox"}'

# Queue: returns request_id, status_url, response_url, cancel_url
curl -X POST https://queue.fal.run/my-org/my-app \
  -H "Authorization: Key $FAL_KEY" -H "Content-Type: application/json" \
  -d '{"prompt": "a red fox"}'
curl "$STATUS_URL?logs=1" -H "Authorization: Key $FAL_KEY"
curl "$RESPONSE_URL" -H "Authorization: Key $FAL_KEY"
curl -X PUT "$CANCEL_URL" -H "Authorization: Key $FAL_KEY"

# Webhook instead of polling
curl -X POST "https://queue.fal.run/my-org/my-app?fal_webhook=https://example.com/hook" \
  -H "Authorization: Key $FAL_KEY" -H "Content-Type: application/json" -d '{"prompt": "a red fox"}'
```

The webhook receiver must verify the ED25519 `X-Fal-Webhook-Signature` against the keys
at `https://rest.fal.ai/.well-known/jwks.json` and check the timestamp before trusting
the payload: https://fal.ai/docs/documentation/model-apis/inference/webhooks

Queue states: `IN_QUEUE` (with `queue_position`), `IN_PROGRESS` (with logs if requested),
`COMPLETED` (also the terminal state for failed requests: check the response for an
error). Queue requests are retried after a runner 503/504, a runner disconnect or
incomplete response, a `request_timeout`, or a gateway-to-runner connection error (up to
10 attempts total; tune with `skip_retry_conditions` / `retry_config`, e.g.
`skip_retry_conditions = ["timeout"]` so long jobs are not re-run). The platform never
retries direct `fal.run` calls.

## CLI smoke test

```bash
fal api my-org/my-app prompt="a red fox" steps=4
```

## Testing during development

1. `fal run app.py::MyApp --auth private` boots the app on real hardware and prints a
   Playground URL and `Sync`/`Async` API URLs for each endpoint. The app is ephemeral
   (deleted when the process exits), bills while it runs, and is **public** without
   `--auth private`. Run it in the background, hit the printed URL with curl (with
   `Authorization: Key $FAL_KEY`) once `Application startup complete` appears, then stop
   the process. This runs `setup()` exactly
   as a deploy would: always do it before the first `fal deploy`.
2. `fal run --local app.py::MyApp` serves the app on your machine at
   `http://localhost:8080` (`--exposed-port` to change). You provide the dependencies and
   hardware.
3. Automated test against an ephemeral deployment:

```python
import fal
from app import MyApp, Input

def test_generate():
    # startup_timeout defaults to 60 s; cover setup() (model download and load).
    with fal.app.AppClient.connect(MyApp, startup_timeout=900) as client:
        out = client.generate(Input(prompt="a red fox"))   # method named after the endpoint function
        assert out.image.url
```

`AppClient.connect(MyApp)` spawns the app, waits for `/health`, and exposes each endpoint
as a method that takes **one argument**: a Pydantic model or a dict of the input fields.
It calls the endpoint's return annotation with the response fields, so that must be a
Pydantic model class evaluated at runtime (no `from __future__ import annotations` in the
app module); with no annotation it returns the raw dict. The app is spawned with the
class's `app_auth` (**public** if unset), and requests authenticate only with a key
(`FAL_KEY` or a profile key), not the `fal auth login` session. Set `app_auth = "private"`
and export `FAL_KEY` for tests.

Calling other fal endpoints from inside an app: `FAL_KEY`, a key scoped to the app
owner's account, is set automatically when the app runs with privileged access (the
default for deployed apps), so `fal_client.subscribe(...)` works with no configuration.
It is injected at runtime only, not during the image build. Every call made with it is
billed to the owner, not to whoever called your app: a **public** (or `shared`) app that chains
`fal_client` calls lets any caller spend the owner's credits. Prefer private for such
apps, and confirm the exposure with the user before deploying one that is not.

Docs:
- https://fal.ai/docs/documentation/development/calling-your-endpoints
- https://fal.ai/docs/documentation/development/test-models-and-endpoints
- https://fal.ai/docs/documentation/model-apis/inference/queue
