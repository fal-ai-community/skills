# fal Creative Suite for OpenClaw

Create images, video, audio, 3D, product campaigns, game assets, short films,
product photos and localized media with fal. This bundle includes the complete
canonical library and its companion skills, scripts, references and assets.

Generation uses your connected fal account and its credits. A browser sign-in
connects that account; no API key is included or required. Local editing and
composition require the tools described by the selected workflow.

## Install and connect

After the ClawHub release is public, install the package:

```sh
openclaw plugins install clawhub:@fal-ai-community/creative-suite
openclaw plugins inspect fal-ai
```

The bundle declares the public fal MCP endpoint with Streamable HTTP and OAuth.
Use **Settings → MCP → Sign in** to authorize fal. For native CLI setup, preserve
an existing fal connection and follow the public setup guide:

https://github.com/fal-ai-community/skills/blob/main/docs/distribution.md#openclaw

The included `mcp.config.json` is a merge fragment, not a replacement for existing
settings. If your client does not expose the bundle server for sign-in, add that
native connection before authorization. Confirm tool discovery before generation.

## Start a workflow

- Create a product ad campaign from a brief and reference photos.
- Produce a consistent game asset pack with transparent exports.
- Turn an approved storyboard into a short film.
- Produce e-commerce product photographs and platform crops.
- Localize an approved video and adapt it for new placements.

Ask fal to select current models and check schemas and prices before spending.
The bundle's skills load on demand. Install the bundle as a unit so companion
skills remain available. Do not publish individual skill folders as independent
workflows without their dependencies.

## Source and license

Canonical source: https://github.com/fal-ai-community/skills

`skills-source.lock.json` records the exact source commit and skill index hash.
The MIT license and copyright notice are included in `LICENSE`. This package has
no installation scripts, hooks, credential values or native runtime entrypoint.
