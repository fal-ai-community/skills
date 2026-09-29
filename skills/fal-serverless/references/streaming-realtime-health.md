# Multiple endpoints, streaming, realtime, health checks, cancellation

## Multiple endpoints

```python
class MyApp(fal.App):
    @fal.endpoint("/")
    def generate(self, input: GenerateInput) -> GenerateOutput: ...

    @fal.endpoint("/enhance")
    def enhance(self, input: EnhanceInput) -> EnhanceOutput: ...
```

Non-root paths are appended to the endpoint id: `my-org/my-app/enhance`
(`https://fal.run/my-org/my-app/enhance`, `https://queue.fal.run/my-org/my-app/enhance`).
One function can carry only one route. `GET /health` is added automatically.

## Streaming (Server-Sent Events)

The clients (`fal_client.stream`, JS `fal.stream`) default to `path="/stream"`, so use
`@fal.endpoint("/stream")` unless callers pass a matching `path=`.

```python
import json
from fastapi.responses import StreamingResponse

class MyApp(fal.App):
    @fal.endpoint("/stream")
    def stream(self, input: Input) -> StreamingResponse:
        def events():
            for step, preview in self.generate_steps(input):
                yield f"data: {json.dumps({'step': step, 'image': preview})}\n\n"
        return StreamingResponse(events(), media_type="text/event-stream")
```

- Each event is `data: <json>\n\n` (the blank line is required by SSE).
- For image previews use `{"image": {"url": "data:image/jpeg;base64,...", "content_type": "image/jpeg"}}`
  so the Playground renders them; inline data URIs avoid a CDN upload per frame.
- Throttle events (e.g. every N steps) and use low-quality previews.
- If a synchronous pipeline produces events through a callback, run it in a thread and
  hand events to the generator through a `queue.Queue` with a `None` sentinel. Put the
  sentinel in `finally`, or a pipeline exception leaves the stream hanging:

```python
def worker():
    try:
        pipeline(..., callback=lambda e: q.put(e))
    except Exception as e:
        q.put({"error": str(e)})
    finally:
        q.put(None)
```

  The generator should yield an error event (or raise) when it gets one.
- Streaming is a direct connection: it is never retried by the queue, and dropping the
  connection cancels the request.

Test with `for event in fal_client.stream("my-org/my-app", arguments={...}): ...`, or
`curl -N -X POST https://fal.run/my-org/my-app/stream -H "Authorization: Key $FAL_KEY" -H 'Content-Type: application/json' -d '{"prompt": "a red fox"}'`.
Do not test streams with `fal api .../stream`: it prints events only after the stream
ends and gives up after 5 s without data.

## Realtime (WebSocket, msgpack)

```python
from fastapi import WebSocket

class MyApp(fal.App):
    @fal.realtime("/realtime")
    def realtime(self, input: Input) -> Output:          # one message in, one out
        return Output(text=self.model(input.prompt))

    @fal.endpoint("/ws", is_websocket=True)             # raw FastAPI WebSocket
    async def ws(self, websocket: WebSocket) -> None:
        await websocket.accept()
        msg = await websocket.receive_text()
        await websocket.send_text(msg.upper())
        await websocket.close()
```

- `fal_client.realtime("my-org/my-app")` connects to `/realtime` by default (override
  with `path=`), so use `@fal.realtime("/realtime")` unless callers pass a matching
  custom path.
- `@fal.realtime(path, *, buffering=None, session_timeout=None, input_modal=..., output_modal=..., max_batch_size=1, content_type="application/msgpack", encode_message=None, decode_message=None)`.
- Raw sockets: `fal_client.ws_connect("my-org/my-app", path="/ws")` (and `ws_connect_async`).
- Apps with websocket routes get `websockets` and `msgpack` added to their requirements.
- The Playground cannot exercise WebSocket endpoints; test with the client and watch the
  dashboard Logs page. Scaling parameters apply to WebSocket apps unchanged.

## Health checks

```python
class MyApp(fal.App):
    @fal.endpoint(
        "/health",
        health_check=fal.HealthCheck(
            start_period_seconds=30,   # failures ignored while the runner is younger (raised to startup_timeout if lower)
            timeout_seconds=5,
            failure_threshold=3,       # consecutive failures before the runner is replaced
            call_regularly=True,       # every 15 s; False = only when triggered
        ),
    )
    def health(self) -> dict:
        if not self.client.is_alive():
            raise RuntimeError("lost upstream connection")   # raising = unhealthy
        return {"status": "ok"}
```

- Only one health-check endpoint per app, and it cannot be a websocket endpoint.
- It can run concurrently with requests: keep it cheap, no GPU work.
- Any endpoint can force an immediate check by setting the response header
  `x-fal-runner-health-check: true` (take a `response: fastapi.Response` parameter). A
  failed forced check terminates the runner immediately.
- With `call_regularly=False`, `failure_threshold` and `start_period_seconds` are ignored.

## Cancellation

- A queued request that is cancelled never runs. For a running request, fal calls
  `<endpoint path>/cancel` on the same runner with the same `x-fal-request-id` header.
- Direct connections (`run`, stream, realtime) are cancelled when the caller disconnects.
  Queue requests (`submit`/`subscribe`) stop only through the cancel API
  (`handler.cancel()` or `PUT https://queue.fal.run/<app>/requests/<request_id>/cancel`).

```python
import asyncio
import fastapi
from fal.exceptions import RequestCancelledException

class MyApp(fal.App):
    def setup(self):
        self._tasks: dict[str, asyncio.Task] = {}

    @fal.endpoint("/predict")
    async def predict(self, input: Input, x_fal_request_id: str | None = fastapi.Header(None)):
        if not x_fal_request_id:
            raise fastapi.HTTPException(400, "x-fal-request-id is required")
        task = asyncio.create_task(self._generate(input))
        self._tasks[x_fal_request_id] = task
        try:
            return await task
        except asyncio.CancelledError:
            raise RequestCancelledException("Request cancelled")   # -> 499, runner stays healthy
        finally:
            self._tasks.pop(x_fal_request_id, None)

    @fal.endpoint("/predict/cancel")
    async def predict_cancel(self, x_fal_request_id: str | None = fastapi.Header(None)):
        if not x_fal_request_id:
            raise fastapi.HTTPException(400, "x-fal-request-id is required")
        task = self._tasks.get(x_fal_request_id)
        if task and not task.done():
            task.cancel()
```

Cancellation is cooperative: a blocking synchronous GPU call keeps running until it
returns. Check a flag between steps in long loops.

## Graceful shutdown

```python
import threading

from fastapi.responses import JSONResponse

class MyApp(fal.App):
    termination_grace_period_seconds = 60

    def setup(self):
        self.stop = threading.Event()
        self.db = connect_db()   # a resource teardown() releases

    @fal.endpoint("/")
    def run(self, input: Input) -> Output:
        for step in range(input.steps):
            if self.stop.is_set():
                # Unfinished work is not a success: 503 lets the queue retry it on
                # another runner.
                return JSONResponse(status_code=503, content={"detail": "runner shutting down"})
            ...
        return Output(...)

    def handle_exit(self):      # called on SIGTERM
        self.stop.set()

    def teardown(self):         # after in-flight requests finish, within the grace period
        self.db.close()
```

Only queue requests are retried; a direct `fal.run` caller receives the 503.

## Status codes that change platform behaviour

Return errors with `fastapi.responses.JSONResponse(status_code=..., content={"detail": ...})`.

| Return | Runner | Queue retry |
|---|---|---|
| 4xx | kept | no |
| 500 / 502 | health-checked, replaced if the check fails | no |
| 503 | **stopped immediately** | yes, on another runner |
| 504 | health-checked | yes |

- Use 400/422 for bad input and 500 for a failed inference on a healthy runner. Reserve
  503 for a runner that is truly broken (GPU OOM, corrupted state).
- Response headers: `X-Fal-Needs-Retry: 1|0` forces or prevents a retry (honoured only
  on 5xx and 429); `x-fal-stop-runner: true|false` forces or prevents runner termination
  regardless of status.
- Queue retries go up to 10 attempts total. App-level control: `skip_retry_conditions`
  and `retry_config` (see `app-configuration.md`).

Docs:
- https://fal.ai/docs/documentation/development/streaming
- https://fal.ai/docs/documentation/development/realtime
- https://fal.ai/docs/documentation/development/add-health-check-endpoint
- https://fal.ai/docs/documentation/development/handle-cancellations
- https://fal.ai/docs/documentation/serverless/reliability/retries
