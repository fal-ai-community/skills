# Local video compositing

Assemble existing footage, images, audio and exact text with a local renderer.
Do not regenerate the user's footage to add a caption, logo or transition.

## Runtime and public dependencies

Use a renderer available in the user's environment. One public option is
[Hyperframes](https://github.com/heygen-com/hyperframes); follow its current
installation and CLI documentation. Python, Node, a browser, fonts and ffmpeg
are dependencies to check, not services bundled with this skill. Use a supported
local tool if Hyperframes is absent. Do not assume a hosted execution tool or a
particular absolute workspace path exists.

## Workflow

1. Record source assets, requested duration, aspect ratio, frame rate, exact copy,
   logo files and audio treatment. Keep originals unchanged.
2. Create a local project directory and place approved assets under `assets/`.
   Use relative paths in the composition. Follow the renderer's current project
   format and check its version-specific command help before execution.
3. Build the timeline from the actual clips. Use real text and original logo assets
   for overlays. Match source frame rates where possible; avoid stretching footage.
4. For speech captions, transcribe the demuxed audio with a currently accessible
   timed speech endpoint. Filter non-word tokens and group captions by actual
   timestamps. Read `fal-audio-generation` and `fal-motion-graphics` as needed.
5. Run the renderer's available checks, then make a short draft. Inspect overlays,
   safe areas, timing and fonts before the final export. Large jobs may render in
   matching scene segments and join locally with ffmpeg.
6. Render the final MP4, probe its duration, dimensions, streams and frame rate,
   watch the transitions, and listen to the mix. Keep the editable project.
7. Return the output file with the client's normal file interface. If an upload
   is requested, use a destination authorized by the user. Do not assume an asset
   card, private library, automatic upload or hosted retention service exists.

Only generate missing media when the brief requires it. Discover models through
genmedia or the connected public fal MCP tools, inspect current schemas and prices,
and check the user's actual account access before a paid call.
