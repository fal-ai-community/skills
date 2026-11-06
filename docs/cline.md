# Connect fal to Cline

Connect Cline to the [hosted fal MCP](https://fal.ai/mcp) to discover models,
check prices, and produce images, video, audio, and 3D assets.
Sign in with your fal account through browser OAuth.

## Cline extension

1. Open **MCP Servers** in the Cline panel.
2. Open **Remote Servers**.
3. Enter the name `fal`.
4. Enter `https://mcp.fal.ai/mcp-relay` as the server URL.
5. Select **Streamable HTTP** and add the server.
6. Complete the OAuth authorization when Cline requests it.
7. Confirm that Cline lists the fal tools.

If you configure JSON directly, add this entry to the existing `mcpServers`
object. Preserve your other servers:

```json
{
  "mcpServers": {
    "fal": {
      "type": "streamableHttp",
      "url": "https://mcp.fal.ai/mcp-relay",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Use Cline's **Configure MCP Servers** button to find the correct settings file.
The extension and CLI use separate settings locations.
Keep `autoApprove` empty so Cline retains its tool approval controls.

## Cline CLI

With Cline CLI installed, add the remote connection:

```sh
cline mcp add fal https://mcp.fal.ai/mcp-relay --transport http --yes
cline config mcp --json
```

Run `cline mcp` and use **Authorize OAuth** for `fal` when authorization is
required. Complete the browser sign-in before you request tool execution.

## Verify the connection

Ask Cline:

> Use fal to find image models and inspect a candidate's input schema and
> published prices. Do not generate media.

Check that the response comes from fal tools. A saved configuration alone does
not prove authorization or tool discovery.

Then try an outcome brief:

> Plan three product photos for a reusable water bottle: a white-background
> hero, a material detail, and a lifestyle image. Inspect the available models
> and prices. Present the plan and estimated cost before generation.

Media generation can consume fal credits. Follow the user's approved budget.
Submit each approved request once. Keep its job identifier for status checks.
Use the returned media links when the client cannot display an inline preview.

## Troubleshooting

- For HTTP 401, complete or repeat OAuth authorization in Cline.
- For a transport error, confirm `streamableHttp` and the complete relay URL.
- If tools do not appear after authorization, reconnect the server and inspect
  Cline's connection diagnostics.
- If an administrator restricts remote servers, request access through that
  workspace's normal configuration process.

These instructions follow the [Cline MCP guide](https://docs.cline.bot/mcp/mcp-overview).
Marketplace submission and full browser sign-in testing are separate from
configuration validation. This repository does not publish a Cline listing.
