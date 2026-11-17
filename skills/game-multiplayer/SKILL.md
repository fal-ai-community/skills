---
name: game-multiplayer
description: "Make a browser game built with fal assets online multiplayer: keep rules server-ready, keep generated assets in the page, add matchmaking and one server per match. Use when a fal game should get Find Match or online play."
---

# Game multiplayer

> **Runtime:** Asset steps run through the [genmedia CLI](https://github.com/fal-ai-community/genmedia-cli) as in `fal-gamedev`, `game-asset-production` and `fal-regenerate-3d`. The game server and matchmaker in the worked example run on [Edgegap](https://edgegap.com) through its MCP server; any host that can run a Node.js container per match fits the same shape.

fal generates a game's media while it is **built**. A multiplayer match needs one more thing while it is **played**: a server that owns the rules, so no player's browser decides who won. A match makes no fal call, and the server needs no fal asset. Use this skill before the game is written when you can: the structure below costs nothing on day one and avoids a rewrite.

## Rules that make a fal game server-ready

1. **All rules in one file with no browser code.** `rules.js` as an ES module: no `window`, `document`, canvas, WebGL, audio or timers. Export `createWorld()`, `addPlayer(world, id, name, isBot)`, `removePlayer(world, id)`, `setInput(world, id, input)` with plain numbers and booleans, `step(world, dt)` returning a list of events, and `botInput(world, id)` reading only positions. The page runs it for solo play; the server imports the same file.
2. **Collide with numbers, not meshes.** A character is a circle, a wall is a box, a reach is a distance. Never read a size from a generated model: scale the model to the rule in the renderer.
3. **Every asset optional.** List models, textures and sounds in one `assets.js`; draw a plain shape when an entry is empty or fails to load. The game is then playable and testable, online included, before any credit is spent.
4. **One draw path.** The renderer draws a plain view object (`{players, items, ...}`) built from the local world in solo play or from server snapshots online.
5. **Design for delay.** Pushing, carrying, a bit of slide, slow projectiles and turns hold up without client prediction. Precise platforming and instant-hit aiming do not.

## Generated assets in a multiplayer game

- **Characters:** concept image, then image-to-3D with rigging (see `fal-regenerate-3d`). Ask the image for a full body in an A-pose, separated limbs and empty hands so the auto-rig works. Rigging can return walk and run clips as separate armature-only GLBs: load them and play them on the rigged model, the bone names match.
- **Sizing a rigged GLB in Three.js:** its nodes carry their own scale, so `Box3.setFromObject(model)` can be about 100 times off. Call `model.updateMatrixWorld(true)` and `box.setFromObject(model, true)` to measure the skinned vertices. Clone per player with `SkeletonUtils.clone`.
- **Sprites (`fal-gamedev`, `game-asset-production`):** frame geometry belongs to the page; hit boxes belong to `rules.js`.
- **Sounds:** one short clip per rules event. Play them from the events `step()` returns, which the server forwards online, so both modes sound the same.
- **Nothing goes in the server image.** It holds the server code and `rules.js`. New art needs no server release; only a rules change does.

## Going online

The server is small: accept WebSocket players, clamp every input field, run `botInput` for bots, call `step()` at a fixed rate, send rounded positions and events 20 times a second, end on the rules' winner and stop.

A worked, verified example: [edgegap/netcode-sample-fal-relic-rumble](https://github.com/edgegap/netcode-sample-fal-relic-rumble), a Three.js game for 4 with four rigged characters, props, a floor and sounds generated on fal (prompts, models and prices in its `PROMPTS.md`). Its server is one Node.js container per match that stops itself after the match, started by a matchmaker for 2 to 4 players with bots in the empty seats. Two headless players and two browser tabs were matched onto one server and played a full match on 2026-11-17.

To do the same for the user's game with a coding agent, connect the Edgegap MCP server (`https://mcp.edgegap.dev`, repository [edgegap/llm-mcp-server](https://github.com/edgegap/llm-mcp-server)) and load its `edgegap-fal` skill: it has the server templates, the container build, the matchmaker config and the end-to-end tests. The user creates the Edgegap account and matchmaker; never ask for an API token in chat.

## Checks

- `grep -nE "window|document|canvas|setTimeout|setInterval|requestAnimationFrame" rules.js` prints nothing.
- The game plays with `assets.js` emptied.
- Two headless players finish a full match on a local server before anything is deployed.
- After testing, no match server is left running.

## Out of scope

Interactive world models, where the world is generated video, have no game server to host.
