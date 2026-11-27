# Art audit — before the site goes public

Status as of the import (2026-11-26). Nothing here is legal advice. The FFG/Asmodee fan-content
policy check is still to do and may change some of these calls.

| Asset | Where | Source | Risk | Action |
|---|---|---|---|---|
| 24 faction portraits | `assets/factions/portraits-REVIEW/` (Ledger used them) | **Official FFG card/box artwork.** Two (Argent, Vuil'raith) still show "© Fantasy Flight Games … Artist: Anders Finér" on the image. | **High** | Don't deploy. Replace with original cinematic portraits, or drop portraits until the policy check says otherwise. |
| 24 small emblems | `assets/factions/emblems/` (Ledger) | Look like the official faction symbols, rendered glossy. Source not recorded. | **Medium–High** | Prefer replacing with original emblems. |
| 24 pixel-art emblems | `assets/factions/emblems-px/` (Arbiter) | Labelled in the Arbiter as "original designs for this app", but they closely follow the official symbol shapes. | **Medium** | Fine to keep while testing privately. Decide after the policy check; a redesign that doesn't trace the official shapes is the safe route. |
| 11 unit sprites + frames | `assets/units/` (all three tools) | Renders of "Twilight Imperium 4 ship models" by Saunick, thingiverse.com/thing:4191414, **CC BY**. | Low | Keep. Attribution must stay visible (NOTICE.md + footer). |
| Objective scene art | `ledger/scenes.js` | Generated SVG, written for the Ledger. | Low | Keep. |
| Agenda card scenes | inside `council/index.html` | Generated SVG, written for the Council. | Low | Keep. |
| Speaker token | inside the Ledger | Generated SVG (red/grey enamel hexagon). | Low | Keep. |
| Game text | all modules | Paraphrased rules, card names, faction names. | Low–Medium | Card names/short rules summaries are common in fan tools; confirm against the policy. |
| Names "Twilight Imperium", faction names | all modules | FFG trademarks. | — | Use descriptively with the "fan-made, not affiliated" notice. Don't put them in the site's own name or logo. |

## Before going public

- [ ] Read the current FFG / Asmodee fan-content policy and record the link and date here.
- [ ] Replace or remove the 24 portraits.
- [ ] Decide on the emblems (replace, or keep the pixel-art set if the policy allows).
- [ ] Footer on every page: fan-made notice + CC BY credit for the unit sprites.
- [ ] No ads, no donations tied to FFG content, no paid tier.
