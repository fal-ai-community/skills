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
fal_client.subscribe("my-org/my-app/enhance", arguments={...})
fal_client.subscribe("my-org/my-app", arguments={...}, path="/enhance")

# Fire and poll later
handle = fal_client.submit("my-org/my-app", arguments={"prompt": "a red fox"})
print(handle.request_id, handle.status())
result = handle.get()
handle.cancel()

# Direct call: no queue, no retries, no status
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
`client_timeout=` (client-side wait only), `priority="low"`, `hint=` (runner affinity),
`webhook_url=` (`submit` only).

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
  -H "Authorization: Key $FAL_KEY" -H "Content-Type: application/json" -d '{...}'
```

Queue states: `IN_QUEUE` (with `queue_position`), `IN_PROGRESS` (with logs if requested),
`COMPLETED`. Queue requests are retried on 503, 504 and connection failures (up to 10
attempts); direct `fal.run` calls never are.

## CLI smoke test

```bash
fal api my-org/my-app prompt="a red fox" steps=4
```

## Testing during development

1. `fal run app.py::MyApp` boots the app on real hardware and prints a Playground URL and
   `Sync`/`Async` API URLs for each endpoint. The app is ephemeral (deleted when the
   process exits) and **public** unless you pass `--auth private`. Hit the printed URL
   with curl once `Application startup complete` appears. This runs `setup()` exactly
   as a deploy would: always do it before the first `fal deploy`.
2. `fal run --local app.py::MyApp` serves the app on your machine at
   `http://localhost:8080` (`--exposed-port` to change). You provide the dependencies and
   hardware.
3. Automated test against an ephemeral deployment:

```python
import fal
from app import MyApp, Input

def test_generate():
    with fal.app.AppClient.connect(MyApp) as client:
        out = client.generate(Input(prompt="a red fox"))   # method named after the endpoint function
        assert out.image.url
```

`AppClient.connect(MyApp)` spawns the app, waits for `/health`, and exposes each endpoint
as a method that takes **one argument**: a Pydantic model or a dict of the input fields.
It returns the endpoint's annotated return type.

Calling other fal endpoints from inside an app: `fal_client.subscribe(...)` works with
no configuration because `FAL_KEY` is injected on every runner. Those calls are billed to
the app owner.

Docs:
- https://fal.ai/docs/documentation/development/calling-your-endpoints
- https://fal.ai/docs/documentation/development/test-models-and-endpoints
- https://fal.ai/docs/documentation/model-apis/inference/queue
