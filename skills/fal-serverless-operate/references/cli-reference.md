# fal CLI reference for operating apps

Generated from the argparse definitions in the `fal` package. Run `fal <cmd> --help` to
confirm on the installed version. Almost every command accepts `--team TEAM` (ignored
when a key is in use; see below); commands
marked **env** also accept `--env ENV` (default `main`, or the `FAL_ENV` variable).
Commands marked **json** accept `--json` (same as `--output json`) for machine-readable
output. Every command also accepts a hidden `--debug` flag that prints full tracebacks.

## Auth, accounts, profiles, doctor

```bash
fal auth login [--connection github|google|<sso-domain>] [--no-browser]
fal auth logout
fal auth whoami
fal account list | fal account set <account> | fal account unset     # aliases: accounts, team, teams
fal profile list | set <PROFILE> | unset | key | host | create | delete
fal doctor [--json]      # fal/isolate version, Python, platform, FAL_HOST, and the key id from the FAL_KEY env var (blank unless FAL_KEY is set)
```

Key credentials take precedence over the login session, in this order: a
`FAL_KEY=<key_id>:<key_secret>` environment variable, the active profile's key, then
`FAL_KEY_ID`/`FAL_KEY_SECRET`. With a key, `--team` and `fal account set` are ignored:
commands act on the account the key was created under. To act on a team, use a key
created for that team, or unset the key (or set `FAL_FORCE_AUTH_BY_USER=1`) and use the
login session. `FAL_PROFILE` selects a profile. `fal auth whoami` shows the account in
use.

## Apps (`fal apps`, alias `fal app`)

| Command | Flags |
|---|---|
| `fal apps list` | **env** **json** `--filter TEXT` (alias contains), `--sort-by-runners`, `--regions R [R ...]` |
| `fal apps list-rev [app_name]` | **env** |
| `fal apps set-rev <app_name> <app_rev>` | **env** `--auth {public,private,shared}` `--strategy {recreate,rolling}` |
| `fal apps scale <app_name>` | **env** `--keep-alive N` `--max-multiplexing N` `--max-concurrency N` `--min-concurrency N` `--concurrency-buffer N` `--concurrency-buffer-perc N` `--scaling-delay N` `--request-timeout N` `--startup-timeout N` `--machine-types T [T ...]` `--regions R [R ...]` (replaces the region list; include the current regions to widen it) |
| `fal apps rollout <app_name>` | **env** `--force` (kill runners immediately, drops in-flight requests) |
| `fal apps runners <app_name>` | **env** **json** `--since 30m|1h|1d|<ISO>` (max 24 h, adds terminated runners) `--state {all,idle,running,pending,setup,crash_backoff,terminated} [...]` |
| `fal apps gpus <app_name>` | **json** |
| `fal apps delete <app_name>` | **env**. Permanent. |
| `fal apps delete-rev <app_rev>` | Takes only the revision id. The active revision cannot be deleted. |

Regions: `eu-north`, `eu-west`, `us-central`, `us-east`, `us-west`.

## Runners (`fal runners`, alias `fal machine`)

| Command | Flags |
|---|---|
| `fal runners list` | **json** `--since ...` `--state ...` (same values as `apps runners`). Lists runners across all apps. |
| `fal runners logs <runner_id>` (alias `log`) | **json** `--search TEXT` `--since T` `--until T` `--follow/-f` `--lines/-n N` (`+N` = oldest N; ignored with `--follow`) |
| `fal runners stop <runner_id>` | `-r/--replace` spawn a replacement first. Graceful. |
| `fal runners kill <runner_id>` | Immediate. |
| `fal runners shell <runner_id>` | Interactive shell in the runner's container (env vars, `/data`, GPUs visible). |
| `fal runners exec <runner_id> [-it] -- <command ...>` | Run one command. Put `--` before a command that starts with `-`. `-it` allocates a TTY. |
| `fal runners gpus` | **json**. GPU usage summary across runners. |

Time values for `--since` / `--until`: `now`, relative (`30m`, `1h`, `1d`), or an ISO
timestamp. Without `--since`, `logs` starts at runner start time (or 1 minute ago with
`--follow`).

## Deploy and run

```bash
fal run <file.py::Class | pyproject-app-name> --auth private [--env ENV]
        [--app-name NAME] [--machine-type TYPE] [--no-cache]
        [--local [--exposed-port 8080] [--exposed-metrics-port 9090]]   # port flags need --local
        [--limit-max-requests N]
fal deploy [<file.py[::Class]> | <pyproject-app-name>] [--env ENV] [--app-name NAME]
        [--auth AUTH] [--strategy rolling|recreate] [--attach | --detach]
        [--reset-scale | --no-scale] [--check] [--yes] [--message MSG]
        [--annotation KEY=VALUE]... [--no-cache] [--json]   # repeat --annotation once per pair
```

- `fal run` creates an ephemeral app that is deleted when the process exits and bills
  while it runs. It ignores `app_auth` and pyproject `auth` and, without `--auth`, is
  **public**: anyone with the URL can call it on your bill. Always pass
  `--auth private` unless the user wants a public demo. From an agent, run it in the
  background (or with `--limit-max-requests N`) and stop it when done.
- `fal deploy` defaults to `private` auth and the `rolling` strategy.
- `fal deploy` accepts `--app-name` and `--auth` only with a file reference; with a
  pyproject app name it raises an error, so set `name` / `auth` in
  `[tool.fal.apps.<name>]` instead. `fal run` accepts both flags with a pyproject app
  name, and they override the table.
- `--no-scale` is the default (inherit the live scale settings); `--reset-scale`
  applies the values in code. With a pyproject app name, `--reset-scale` and
  `--strategy` are silently ignored; use `app_scale_settings` / `deployment_strategy`
  in the pyproject table.
- `--check`, `FAL_DEPLOY_CHECK=true`, or a team policy set by an admin prints a
  pre-deploy diff and requires typing `confirm` before deploying. In a non-interactive
  shell (agents, CI) it exits 1 without deploying unless `--yes` is passed, and `--yes`
  deploys without asking. Show the diff to the user before adding `--yes`.
- `--detach` returns once the new revision is registered: traffic moves to it while its
  runners start, and a failed rollout is not rolled back.
- `--force-env-build` is deprecated; use `--no-cache`.
- `FAL_URL_OUTPUT=all|playground|none` (default `all`) controls which URLs `fal deploy` /
  `fal run` print: `playground` keeps the browser links (Playground, app overview) and
  hides the Sync/Async API URLs; `none` prints no URLs.

## Queue

```bash
fal queue size <app_name> [--by-user] [--json]     # app name without the owner prefix
fal queue flush <app_name> [--caller-user-id USER_ID]
```

`fal queue` has no `--env` flag and always acts on the app in the `main` environment;
do not use it for an app in another environment (use the dashboard). `flush` drops
every pending request (or only one caller's) and cannot be undone; it does not touch
requests already running. Confirm with the user that the production queue is the
target.

## Secrets, keys, environments, files

```bash
fal secrets set NAME=VALUE [NAME=VALUE ...] [--env ENV] [--not-exposed-by-default]   # user runs it; never pass real values yourself
fal secrets list [--env ENV]
fal secrets unset NAME [--env ENV]

fal keys create --scope {ADMIN,API} [--desc "CI deploy key"]   # prints FAL_KEY='id:secret' once; deploy/run need ADMIN
fal keys list
fal keys revoke <key_id>

fal environments list                                   # alias: fal envs
fal environments create <name> [--description TEXT]
fal environments delete <name> [--yes]                  # deletes its apps, secrets and history

fal files list [path]                                   # alias: ls. Paths are relative to /data
fal files upload <local_path> <remote_path>             # refuses to overwrite
fal files upload-url <url> <remote_path>
fal files download <remote_path> <local_path>
fal files mv <src> <dst>
fal files rm <path>                                     # recursive
```

## Call an endpoint from the CLI

```bash
fal api my-org/my-app prompt="a red fox" num_images=2 'options[seed]=42'   # quote [] keys in zsh
```

`fal api` submits through the queue and prints the result. Nested keys use
`key[sub]=value` syntax. Every value is sent as a JSON string (`"2"`, not `2`; `:=` does
not change that), so the app's input model must coerce it. A value may not contain `=`
(the CLI crashes), so signed URLs with query strings cannot be passed; use
`fal_client.subscribe(...)` or curl with a JSON body instead. A model id ending in
`/stream` prints events only after the stream ends and gives up after 5 s without data,
so test streams with `fal_client.stream` or `curl -N`.

## Python equivalents

`fal.api.SyncServerlessClient` mirrors the CLI (`client.apps.list()`,
`client.apps.scale("my-app", max_concurrency=10)`, `client.apps.rollout(...)`,
`client.runners.list()`, `client.runners.stop(id)`, `client.secrets.set(name, value)`,
`client.keys.create(...)`, `client.deploy("app.py::MyApp")`).
