# Cold starts, scaling and cost

## What you pay for

Billing is per second, per runner, at the machine type's rate, for every second a
runner is alive: `SETUP` (your `setup()`), `IDLE` (including the whole `keep_alive`
window), `RUNNING`, `DRAINING` and `TERMINATING` (`teardown()`). `PENDING`, image pulls
and `TERMINATED` are free. Multi-GPU runners are billed `num_gpus x duration`. Idle time
is usually the largest lever, and each `min_concurrency` runner is billed 24/7.

A cold start is the time from `PENDING` to `IDLE`: scheduling, image pull, `setup()`
and the health check. It happens when no idle runner is free: on first traffic, after
runners expire during quiet periods, or when a spike exceeds warm capacity.

## Scaling knobs

| Knob | Default | Effect |
|---|---|---|
| `keep_alive` | 60 s | How long an idle runner waits for another request (also applies to a new runner that never gets one). |
| `min_concurrency` | 0 | Runners that always stay up. |
| `concurrency_buffer` | 0 | Warm runners above current demand; wins over `min_concurrency` when higher. |
| `concurrency_buffer_perc` | 0 | Buffer as a percent of request volume; effective buffer = max(this, `concurrency_buffer`). |
| `max_concurrency` | platform limit | Hard ceiling on runners (and spend); more queueing when hit. |
| `scaling_delay` | 0 s | How long a queued request waits before triggering a scale-up. Avoids scaling for blips. |
| `max_multiplexing` | 1 | Requests per runner at once. Needs async or thread-safe handlers and memory headroom. |

Change them live, with no redeploy:

```bash
fal apps scale my-app --keep-alive 300 --min-concurrency 1 --max-concurrency 20
fal apps scale my-app --concurrency-buffer 2 --scaling-delay 15 --env staging
```

- Live changes to `keep_alive`, `min_concurrency`, `max_concurrency`,
  `concurrency_buffer`, `concurrency_buffer_perc`, `scaling_delay`, `request_timeout`
  and `regions` **persist across later deploys**. `fal deploy --reset-scale` discards
  them and applies the code values.
- Live changes to `machine_type`, `max_multiplexing` and `startup_timeout` are temporary:
  the next deploy resets them to the code. `--machine-types` affects only new runners;
  follow it with `fal apps rollout my-app` to move the existing ones. Replacements start
  on top of `max_concurrency`, so expect a short period near double the runner count.

## Recipes

| Goal | Settings |
|---|---|
| Cheapest, sporadic traffic, cold starts acceptable | `min_concurrency=0`, `keep_alive=10..30` |
| Balanced | `keep_alive=60..300`, `concurrency_buffer=1` |
| Latency-critical | `min_concurrency>=1` plus a buffer (`concurrency_buffer=1..2` or `concurrency_buffer_perc=20`) |
| Spiky load, slow setup | `concurrency_buffer` rather than a large `min_concurrency` |
| Protect the budget | always set `max_concurrency` |
| Lightweight router or proxy app | `machine_type="S"`, high `max_multiplexing` |
| GPU has spare memory, async model | `max_multiplexing=2..4` |

Right-size the GPU. Pick the smallest `machine_type` whose VRAM fits the model, and list
fallbacks (`["GPU-H100", "GPU-A100"]`) to cut `PENDING` time.

## Making setup() faster

1. **Weights on `/data`, not in the image.** HuggingFace already caches under
   `/data/.cache/huggingface`. Use `fal.toolkit.download_model_weights(url)` for other URLs.
   The first runner in a region pays the download; later ones read from the node or
   datacenter cache.
2. **Parallel pre-read** of multi-file checkpoints before loading:
   `subprocess.check_call("find /data/models/x -type f | xargs -P 32 -I {} cat {} > /dev/null", shell=True)`.
3. **Small images.** Use `-runtime` bases, `--no-cache-dir`, clean apt lists, and order
   Dockerfile layers from least to most frequently changed.
4. **Share compiled kernels** across runners with the Inductor cache:

```python
from fal.toolkit import synchronized_inductor_cache

class MyApp(fal.App):
    startup_timeout = 900

    def setup(self):
        import torch
        self.model = load_model()
        with synchronized_inductor_cache("my-model/v1"):    # bump the key when the model changes
            self.model = torch.compile(self.model, dynamic=True)
            self.warmup()                                   # warm up INSIDE the block
```

   The cache is stored per GPU type under `/data/inductor-caches/`. The lower-level pair is
   `dir_hash = load_inductor_cache(key)` ... `sync_inductor_cache(key, dir_hash)`.
5. **Warm up in `setup()`** (one dummy inference), so the first real request does not pay
   for lazy initialisation.
6. Caches are evicted over time, so the first cold start after a quiet period is slower.

## Where to look

- Runner churn and states: `fal apps runners my-app --since 1h --state all`.
- Current GPU footprint: `fal apps gpus my-app`, `fal runners gpus`.
- Queue depth: `fal queue size my-app`.
- The dashboard's App Analytics shows request volume, latency percentiles, runner
  utilisation, startup duration and per-app cost. A high idle-to-processing ratio means
  `keep_alive` or `min_concurrency` is too high.

Docs:
- https://fal.ai/docs/documentation/deployment/scale-your-application
- https://fal.ai/docs/documentation/deployment/scaling-configuration
- https://fal.ai/docs/documentation/serverless/optimizations/optimize-cold-starts
- https://fal.ai/docs/documentation/serverless/optimizations/optimizing-costs
- https://fal.ai/docs/documentation/serverless/optimizations/optimize-startup-with-compiled-caches
- https://fal.ai/docs/documentation/serverless/pricing
