# Install the hosted fal MCP in Cline

Use this guide when the user asks you to connect Cline to fal.
The public hosted endpoint is `https://mcp.fal.ai/mcp-relay`.
It uses Streamable HTTP and browser OAuth with a fal account.

For the Cline extension, use **MCP Servers → Remote Servers**. Add `fal` with
the endpoint above and select **Streamable HTTP**. Complete browser OAuth.

For Cline CLI, use:

```sh
cline mcp add fal https://mcp.fal.ai/mcp-relay --transport http --yes
cline config mcp --json
```

Use `cline mcp` to authorize OAuth if the connection requires it.
Preserve all existing servers and settings. If you edit JSON, the remote
entry uses `"type": "streamableHttp"`, the relay `url`, `"disabled": false`,
and `"autoApprove": []`.

Let Cline manage OAuth tokens through its own authorization flow.
Do not request a fal API key for this hosted connection.
Do not enable automatic approval for paid generation tools.

Verify that fal tools appear. Ask for a model search, candidate schema, and
published prices without generation. Report authorization or discovery errors
accurately; a saved settings file is not a completed connection.

Generate media only within the user's approved request and budget. Keep the
job identifier and check its status rather than resubmitting a pending job.

See the [full Cline guide](docs/cline.md) and [public fal MCP page](https://fal.ai/mcp).
