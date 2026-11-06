# Character sheet patterns (production-proven)

## 1. Full AAA design sheet (16:9, three-zone layout)

The worked master — swap the character, keep the structure (hero left / turnaround center / details right, name texts in quotes, closing style + negative tail):

```
Ultra-detailed 16:9 fantasy character design sheet, official AAA fantasy RPG
character bible, clean editorial layout, elegant ivory background with minimal
luxury UI. Character name "NEFRA", title "Desert Oracle", subtitle "A wandering
oracle from the endless dunes, she reads the flow of fate and guides lost souls."

Left panel features a full-body hero illustration of a petite desert priestess
with warm bronze skin, short platinum-white bob hair, golden amber eyes and a
calm mysterious expression. She wears an elegant white-and-gold desert
ceremonial outfit featuring flowing silk veils, asymmetrical layered skirts,
ornate golden jewelry, engraved belts, arm cuffs, anklets and delicate
embroidered patterns. She stands barefoot while holding an ornate
crescent-shaped oracle staff decorated with gold filigree, gemstones and
hanging charms. The overall silhouette feels graceful, sacred and lightweight.

Center panel includes professional turnaround views (Front, Side, Back),
perfectly consistent anatomy, hairstyle, costume and proportions, shown in
neutral pose.

Right panel includes a large head close-up, multiple facial expressions,
close-up panels of the oracle staff, fabric embroidery, jewelry, belts, arm
ornaments, anklets and embroidered pattern details. Include accessory panels
featuring necklace, headpiece, earrings, bracelets and waist ornaments. Add a
refined color palette featuring ivory, sand beige, warm gold, bronze, cream,
light brown, charcoal and metallic gold.

Style: official fantasy RPG character sheet, premium game artbook
illustration, anime realism, elegant fantasy costume design, intricate gold
ornaments, production-ready concept art, clean composition, no watermark, no
logo, no extra limbs, no deformed anatomy.
```

Why it works: every wardrobe item is NAMED (veils, layered skirts, arm cuffs, anklets…) — named items survive across views and downstream calls; the palette swatch panel doubles as the color-grade anchor.

## 2. Clean 4-column turnaround reference (no text — video identity ref)

```
Create a professional character reference sheet of [the character / the person
in the attached image]. Arrange into four vertical columns, each representing
one viewing angle. Each column contains a full-body view on top and a matching
close-up portrait directly beneath it. Columns (left to right): Column 1:
front view (full body above, front portrait below). Column 2: left profile
(full body facing left) with portrait facing left below. Column 3: right
profile (full body facing right) with portrait facing right below. Column 4:
back view, with matching portrait below. Maintain even spacing and framing
around the character. Clean silhouette, consistent alignment, and clean panel
separation. No text. Thin borders. Flat lighting.
```

Use this variant when the sheet will be a reference image (Image N) for video models — text and decoration on the sheet can leak into video frames; flat lighting keeps the identity readable under any scene light.

## 3. Expression sheet

```
Create a character expression sheet showing [character] displaying 12
different emotions arranged in grid format: happy smile, sad tears, angry
frown, shocked surprise, smug grin, embarrassed blush, confused tilt, sleepy
yawn, excited sparkle eyes, nervous sweat, bored deadpan, laughing joy.
```

## 4. From an existing photo/render (edit mode)

Attach the image and scope the edit: "Create a professional character reference sheet of the person in the attached image. Keep the facial features, hair, and outfit exactly the same as Image 1 in every view." — edit endpoints (identity from the upload) beat text re-description every time. For angle-only variants of one render, a multi-angle edit model (96 poses) is cheaper than a full sheet.

## Downstream binding (how other calls consume the sheet)

* Scoped reference clause (video): "Use Image N (the sheet's position in the reference list) only for the character's final identity, wardrobe, and props." — scoping prevents the sheet's layout/background from bleeding into the scene.
* Inline anchor parenthetical (text-only calls): paste the anchor into the prompt where the character first appears — `a desert oracle (character reference "NEFRA": dark skin, white bobbed hair with straight bangs, golden eyes, black-and-gold headband with tasseled gold earrings, white bandeau top with translucent shawl, layered slit skirt with gold plates, gold armlets, collar and anklets, barefoot, golden crescent staff with glowing orb)` — the parenthetical IS the sheet in words; reuse it verbatim in every shot.
* Strict-identity clause (photoreal): "Use the provided reference photo as the STRICT ONLY visual reference for [the subject]. Maintain her exact appearance with zero deviation."
* Token permanence: never paraphrase anchor tokens between calls; "golden amber eyes" must not become "yellow eyes".
* Midjourney route: `--cref [sheet url] --cw 75` (raise to 90 + "exact same outfit" if clothing drifts).
