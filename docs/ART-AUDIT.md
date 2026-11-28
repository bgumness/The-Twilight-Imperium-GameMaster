# Art audit — before the site goes public

Status as of the import (2026-11-26). Nothing here is legal advice. The FFG/Asmodee fan-content
policy check is still to do and may change some of these calls.

| Asset | Where | Source | Risk | Action |
|---|---|---|---|---|
| 24 faction portraits | `assets/factions/portraits/` | Official FFG artwork. Two (Argent, Vuil'raith) carry "© Fantasy Flight Games … Artist: Anders Finér" on the image. | Medium | **Kept (Ben, 2026-11-26)** under the Asmodee NA fan-content guidelines: free, credited, "© Fantasy Flight Games" shown next to every portrait. Revisit if the policy changes. |
| 24 small emblems | removed | The Ledger's original emblems (looked like the official symbols). | — | **Removed 2026-11-26**; the Ledger now uses the Arbiter's symbols. |
| 24 pixel-art emblems | `assets/factions/emblems-px/` (all modules) | Labelled in the Arbiter as "original designs for this app", but they closely follow the official symbol shapes. | **Medium** | Fine to keep while testing privately. Decide after the policy check; a redesign that doesn't trace the official shapes is the safe route. |
| Council Keleres symbol | `assets/factions/emblems-px/keleres.webp` | Original art made for this site (council-of-three motif, same style as the set). | Low | Keep. |
| 11 unit sprites + frames | `assets/units/` (all three tools) | Renders of "Twilight Imperium 4 ship models" by Saunick, thingiverse.com/thing:4191414, **CC BY**. | Low | Keep. Attribution must stay visible (NOTICE.md + footer). |
| Objective scene art | `ledger/scenes.js` | Generated SVG, written for the Ledger. | Low | Keep. |
| Agenda card scenes | inside `council/index.html` | Generated SVG, written for the Council. | Low | Keep. |
| Speaker token | inside the Ledger | Generated SVG (red/grey enamel hexagon). | Low | Keep. |
| Game text | all modules | Paraphrased rules, card names, faction names. | Low–Medium | Card names/short rules summaries are common in fan tools; confirm against the policy. |
| Names "Twilight Imperium", faction names | all modules | FFG trademarks. | — | Use descriptively with the "fan-made, not affiliated" notice. Don't put them in the site's own name or logo. |

## Before going public

- [x] Policy checked 2026-11-26: Asmodee North America "Guidelines for Community Use of Our Intellectual Property" (zmangames.com/ip-policy, linked from fantasyflightgames.com/en/more/legal-information). Fan creations may use game art if freely shared and credited with a copyright notice next to the art. "Online versions of our games" are carved out; a companion tool is not one.
- [x] Portraits kept, with the © notice beside each one.
- [ ] Decide on the emblems (replace, or keep the pixel-art set if the policy allows).
- [ ] Footer on every page: fan-made notice + CC BY credit for the unit sprites.
- [ ] No ads, no donations tied to FFG content, no paid tier.
