# Original worked examples

These examples are invented for this skill. Use them as structural patterns,
not reusable story content.

## Thin premise to silent prompt

Premise: A night custodian in a botanical dome realizes the plants are turning
toward a sealed service hatch.

Planning:

| Decision | Selection |
|---|---|
| Duration | 10 seconds |
| Mode | `t2va` |
| Shot budget | `M(10)=2`; use 2 |
| Causal spine | routine inspection → collective plant motion → hatch flexes |
| Dialogue | none |
| Music | none |

Prompt:

integrated_multimodal_description: [Shot 1] Live-action, cinematic, a wide night shot inside a glass botanical dome frames custodian Imani Vale sweeping a flashlight across misted planting beds; broad leaves remain still until her beam reaches a sealed steel service hatch, then every stem slowly inclines toward it. [Shot 2] At 00:05.500, the camera cuts to a low close shot beside the hatch as Imani's boots stop at the edge of the beam; the rubber seal bows outward once, and her flashlight hand freezes above it.
overall_soundscape: Ventilation hum and condensation ticks fill the dome as soft foliage brushes in one gathering wave; the broom wheels stop, then the hatch seal gives a low rubber groan.
non_diegetic_music: N/A

Checks: two 4.5-second-or-longer spans; no speech; final state is visible;
sound follows the causal sequence.

## Dialogue-bearing prompt

Premise: At dawn, a canal engineer confronts a courier who has delivered a
key made of ice.

Planning:

| Decision | Selection |
|---|---|
| Duration | 12 seconds |
| Mode | `t2va` |
| Shot budget | `M(12)=3`; use 3 |
| Speech reserve | `U=7`; cap `floor(2.5*7)=17` words |
| Dialogue count | 13 words |
| Music | none |

Prompt:

integrated_multimodal_description: [Shot 1] Live-action, cinematic, a wide dawn shot frames an empty canal lock under pale amber light as engineer Mara Quill waits beside the control wheel and a bicycle courier coasts to a stop across the wet concrete. [Shot 2] At 00:04.500, the camera cuts to a tight overhead shot of the courier setting a translucent ice key in Mara's gloved palm; a rain-dark courier with a breathless, bright tenor (S1) warns, <d>[English] It opens once, then forgets the door.</d> [Shot 3] At 00:08.500, a closer shot frames frost spreading across Mara's glove as she closes her fist; (S1) backs toward the bicycle while Mara looks from the melting key to the submerged gate.
overall_soundscape: Water presses steadily against the lock beneath gull calls and the courier's clicking freewheel; the ice key chimes against the glove, then crackles as frost spreads.
non_diegetic_music: N/A

Checks: timestamps are half-second-quantized and below 12; spans are 4.5,
4, and 3.5 seconds; one 13-word line fits the computed cap; S1 is introduced
once.

## First-frame image prompt

Input image state: A copper-suited weather observer stands on a snowy roof at
blue hour, holding a red kite reel; a radio mast rises behind her.

Planning:

| Decision | Selection |
|---|---|
| Duration | 8 seconds |
| Mode | `i2va` |
| Shot budget | `M(8)=2`; use 2 |
| Image anchor | Shot 1 begins in the supplied composition |
| Music | none |

Prompt:

integrated_multimodal_description: For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced. [Shot 1] Live-action, cinematic, a wide blue-hour shot frames the copper-suited observer on the snowy roof with the red kite reel held at her waist and the radio mast behind her; the reel begins turning by itself, drawing its taut line upward into cloud. [Shot 2] At 00:04.500, the camera cuts to a low-angle close shot along the vibrating line as blue sparks race down it toward her gloves; she releases the reel, but it hangs motionless in the air.
overall_soundscape: Thin rooftop wind moves around the mast with a faint cable whistle; the reel ratchets faster, the line thrums, and a dry electrical fizz stops when the reel leaves her hands.
non_diegetic_music: N/A

Checks: exact preamble appears once; Picture 1 is not repeated; Shot 1 starts
from the reference state; both spans exceed 3 seconds.

## Worked 15-second timeline

Premise: In a flooded subway archive, a cartographer discovers that a paper map
is predicting the water's next rise.

Budget:

- `D=15`.
- `M(15)=3`; use three shots.
- Starts: `00:00`, `00:05.500`, `00:11.000`.
- Spans: `5.5`, `5.5`, `4` seconds.
- Final-start ratio: `11/15=0.733`.
- `U=9`; ordinary dialogue cap is `floor(2.5*9)=22` words.
- Actual dialogue: 9 words.

Prompt:

integrated_multimodal_description: [Shot 1] Live-action, cinematic, a wide interior shot frames cartographer Edda Moss wading between tilted archive shelves under green emergency lamps, holding a dry paper transit map above the black water. [Shot 2] At 00:05.500, the camera cuts to an overhead close shot as a blue line draws itself across the map and stops at a station circle; a compact cartographer with a hushed, sandpapery alto (S1) murmurs, <d>[English] That's here. And the ink is still moving.</d> Water begins spilling over the matching shelf marker beside her. [Shot 3] At 00:11.000, a low wider shot frames Edda folding the map into her coat as the blue line races toward the only lit stairwell; she turns and wades after it while the emergency lamps extinguish behind her in sequence.
overall_soundscape: Submerged ventilation drones beneath slow drips and the wash of each step; pencil-dry scratching crosses the map, water slaps the shelf marker, then electrical relays snap dark behind Edda.
non_diegetic_music: N/A

Checks: exact 15-second arithmetic; three distinct causal beats; the spoken
line fits Shot 2; the final shot receives 4 seconds; no score is needed.

## Non-default score case

Premise: A clockmaker releases a roomful of repaired mechanical birds at the
instant the town's power returns. The user explicitly requests a restrained
score beginning with the release.

Reason before prompt: Non-diegetic music is included because the user
explicitly requested a cue synchronized to the release.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, a dim interior shot frames elderly clockmaker Sorin Pell among shelves of dormant brass birds as he lifts the latch on their wire enclosure; only a battery lantern lights his hands. [Shot 2] At 00:05.000, a slow tracking shot follows the first brass bird through the open door as the workshop bulbs flare back to life and dozens of repaired wings unfold behind it. [Shot 3] At 00:09.500, the camera cuts to a wide exterior dusk shot as the flock streams from the attic window above the newly illuminated square; Sorin remains in the warm window, lowering the empty enclosure door.
overall_soundscape: The workshop's close ticking and faint lantern hiss are joined by a latch click and overlapping brass wingbeats; power relays knock on, glass bulbs buzz awake, and the flock's mechanisms recede above the square.
non_diegetic_music: A restrained celesta and bowed-glass pulse enters when the first bird clears the enclosure, opens into slow luminous chords as the flock reaches the square, and remains low beneath the mechanical wingbeats.

Checks: explicit authorization permits score; onset is tied to the visible
release; three legal timestamps spans fit a 14-second prompt.
