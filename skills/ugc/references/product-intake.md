# Product intake for UGC

Fill this card once before scripting or prompting. Every script line, prompt
and claim draws from it, so the product looks and behaves the same in every
clip.

## Canonical product line

One sentence, reused verbatim in every prompt:

```text
[brand/name], [type], [size/volume], [color + finish], [shape/silhouette],
[closure/cap/opening], [visible text on the product, exactly as printed]
```

Example: "<BRAND> 750 ml stainless steel water bottle, matte sage green,
straight cylinder with rounded shoulders, brushed steel screw cap with a carry
loop, white vertical text '<BRAND>' and '750 ml'."

## Usage mechanics

How a person physically uses it, in order. These become the demo beats and
keep hands and motion plausible.

- Hold: grip, size in hand, one or two hands.
- Open/close: twist, flip, pull, press; direction and number of turns.
- Use: pour, apply, wear, plug in, fold; what changes on screen.
- Result the camera can see: condensation, texture, fit in a bag, sound.

For software, record the screen flow instead: the starting screen, the clicks or
inputs in order, and the visible result.

Ask only for mechanics you cannot see in the product photo or screenshots.

## Claim allowlist

Only these may appear as spoken or written claims:

- Claims the user supplied word for word that are observable, or that the
  user confirms are substantiated (`fal-script-writer` Step 3). A health,
  safety, medical, financial, environmental, superlative or comparative claim,
  or any number, rating or performance figure (a size, volume or count printed on the product is an observation; a printed performance, health or safety figure ("SPF 50", "24 h cold") still needs substantiation), without that confirmation stays
  out, even verbatim. The product's own unaltered label may stay visible; an
  unsubstantiated printed figure is never spoken, captioned, zoomed on or
  framed as a claim, and is left out of the canonical line's text field.
- Observations that are true of the real product: shown in media the user
  supplied, or confirmed by the user ("it fits the cup holder" only if a
  supplied photo shows it or the user says so). A generated shot can
  illustrate how the product is used, including a usage step the camera sees
  (pouring, opening, holding); a fit, capacity, temperature, texture, colour or consistency shown on screen
  (fit in a bag, condensation) is an observation and needs the same supplied
  media or user confirmation; it never proves a claim.

Everything else (durations, temperatures, health, savings, "best", reviews,
ratings) stays out unless the user supplies it and it passes the first
bullet. If the user asks for a claim
without proof, write the visible alternative and say why.

## Identity

- Product: one approved product image is the reference for every shot; never
  redraw the logo or label from text.
- Creator: one approved creator image for all clips. A generated creator is a
  host, not a customer: no first-person usage history ("I've used this for
  months"), no "my results", no reported feelings ("I love this"). Present
  tense, demonstrative ("here's", "watch", "you just…").
- Tell the user when the creator is AI-generated, so they can apply their
  platform's AI and ad disclosure rules.
