// 12 distinct design directions inspired by top web-design award winners.
// Each variant spec pushes the model toward a recognizable, highly-designed output.

export const DIRECTIONS = [
  {
    slug: "artistic-universal",
    label: "Artistic Universal",
    vibe: "A considered, timeless, slightly artistic redesign. Everything feels designed on purpose: typography is the primary visual, negative space is load-bearing, nothing is decorative for its own sake. Use a single restrained palette that honors the brand (two or three hues maximum, one accent, never generic SaaS-vibrant). Prefer one strong display voice with a quiet body companion — the display can be a serif with real voice, a bold humanist sans, or a geometric grotesk; pick because it serves the brand, never because it is trendy. Grid is confident but not loud: large hero type that can breathe across columns, tight gutters, deliberate vertical rhythm between sections, content allowed to be small when small is right. Details should feel handled: 1px hairline rules, specific number-alignment, correct hyphenation, real punctuation. Push a touch further than a safe corporate page — asymmetry in the hero, a surprising typographic scale move, an editorial silence where others would add a filler graphic — but nothing chaotic, nothing gimmicky, nothing that age poorly. Imagery (if the site has any) is silent and specific: a single well-framed still rather than a stock-photo collage. The final output should read as something a small, thoughtful studio shipped after arguing every detail. Minimal and artistic, but always cohesive and always in service of the brand's meaning.",
  },
  {
    slug: "swiss-editorial",
    label: "Swiss Editorial",
    vibe: "High-contrast Swiss editorial layout, 12-col grid, rigorous typographic hierarchy, generous whitespace, oversized serif display type mixed with crisp sans, magazine-style spreads, delicate hairline dividers, muted neutrals + single bold accent. Cover-page hero with large wordmark. Feels like a printed art book translated to web.",
  },
  {
    slug: "brutalist-mono",
    label: "Brutalist Monospace",
    vibe: "Hard brutalist layout, raw monospaced typography, black/white with a single neon accent, unapologetic blocky borders, jittery rotated labels, over-specified data readouts, tickers and system logs, deliberate imperfection, ASCII art touches, no rounded corners. award-winning brutalist tech vibe.",
  },
  {
    slug: "kinetic-type",
    label: "Kinetic Typography",
    vibe: "Massive kinetic typography, marquee text strips that scroll horizontally, shifting weight on hover, oversized bold wordmarks that break layout, bold black-and-cream palette with fluorescent accents, CSS animations for type wiggle, scroll-driven effects. award-tier kinetic-type hero.",
  },
  {
    slug: "glass-3d",
    label: "Glassmorphism 3D",
    vibe: "Dreamy glassmorphism with frosted panels, blurred gradient meshes, soft iridescent blobs drifting in background, 3D-feeling pill buttons, subtle parallax, rounded 2xl cards, whispery white-on-gradient copy. Futuristic SaaS landing. Apple-like softness but richer color.",
  },
  {
    slug: "dark-neon-cyber",
    label: "Dark Neon Cyber",
    vibe: "Deep-black background with neon cyan/magenta gradients, thin neon outlines, grid lines, subtle scanlines, cyberpunk-meets-tech aesthetic, big bold condensed sans headings, product shots with glowing edge lights. Cinematic hero with spotlight effect.",
  },
  {
    slug: "magazine-grid",
    label: "Magazine Grid",
    vibe: "Magazine spread layout with asymmetric 12-col grid, pull quotes, big drop caps, mix of serif + sans, rich editorial imagery, caption tags, footnotes. Pale cream background, ink-black text, single red accent. Feels like The New York Times Magazine online.",
  },
  {
    slug: "playful-maximal",
    label: "Playful Maximal",
    vibe: "Playful maximalism, saturated primary colors, chunky rounded type, sticker-style icons, confetti particles, wonky rotated cards, fun cursor trails, winking emojis as section markers. Duolingo-meets-Figma creative energy.",
  },
  {
    slug: "y2k-retro",
    label: "Y2K Retro",
    vibe: "Y2K chrome aesthetic, iridescent holographic gradients, bubble type, ball-bearing reflections, lens flares, retro-futuristic dingbat icons, star sparkle decorations, mid-2000s Windows Media Player vibes with a 2026 twist.",
  },
  {
    slug: "editorial-mono",
    label: "Editorial Monochrome",
    vibe: "Minimal monochrome editorial — pure black on off-white, one oversized serif display face, content-first, extreme whitespace, subtle underlined links, no imagery above the fold except one perfectly-placed photograph. Awards.design understated winner.",
  },
  {
    slug: "scroll-story",
    label: "Scroll-driven Storytelling",
    vibe: "Long-scroll narrative landing. Section-snap scrolling, numbered chapters (01 / 02 / 03), big cinematic quotes, sticky captions, image reveals on scroll (CSS only, no JS libs), moody photography, deep navy + bone palette. Feels like The Pudding meets Airbnb.",
  },
  {
    slug: "terminal-hacker",
    label: "Terminal Hacker",
    vibe: "Full-bleed terminal aesthetic, green-on-black with a twist of amber, blinking cursor, typewriter-style copy reveal, ascii-rendered logos, command-prompt style CTAs like `> deploy_now`. Developer-hype landing page energy.",
  },
  {
    slug: "anime-gradient",
    label: "Anime Gradient",
    vibe: "Soft anime pastel gradients, cloud textures, rounded bubble type, sakura-pink + sky-blue + cream, whisper-light serifs for body, big illustrative icons, floating stars. Feels like a Studio Ghibli landing page designed by Vercel.",
  },
];

export function pickDirections(n) {
  const forced = process.env.FAL_SITE_DIRECTION;
  if (forced) {
    const match = DIRECTIONS.find((d) => d.slug === forced);
    if (!match) {
      throw new Error(`FAL_SITE_DIRECTION="${forced}" does not match any direction slug. Known: ${DIRECTIONS.map((d) => d.slug).join(", ")}`);
    }
    return Array.from({ length: Math.max(1, n) }, () => match);
  }
  const shuffled = [...DIRECTIONS].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, Math.min(n, DIRECTIONS.length));
}
