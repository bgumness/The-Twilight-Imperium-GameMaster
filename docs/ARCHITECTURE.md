# TI4 GameMaster — architecture

Fan-made companion site for Twilight Imperium 4th Edition + Prophecy of Kings.
Three tools, one shared table setup, a static site with no backend.

## 1. What the three tools look like today (imported 2026-11-26)

Originals are kept byte-for-byte in `_import/` for reference and diffing.

| | Ledger | Council Chamber | Battle Arbiter |
|---|---|---|---|
| Source | `_import/ledger/` index.html 222 KB + scenes.js 139 KB + scenes.css 5 KB | `_import/council/index.html` 410 KB, one file | `_import/arbiter/index.html` 827 KB, one file |
| Storage key(s) | `ti4-objective-ledger-v1` (whole game) | `galactic-council-chamber-v1` (game), `…-v1-still` (reduced-motion flag) | `ti4-arbiter-cfg-v1` (current battle setup), `ti4-arbiter-game-v1` (roster, per-faction techs/upgrades, battle stats), `arb_tvzoom`, `ti4-arbiter-display` (TV-link messages) |
| Players | `players[{id:"p1", name, faction:"Federation of Sol", color, hand}]` | `seats[{name, fac:"federation-of-sol", col, flags}]` + `speaker` as a seat index | `GAME.players[{fac:"sol", name, color, upg, techs, flags, tg}]`, keyed by faction, no player id |
| Speaker | `g.speaker` = player id | `speaker` = seat index | — |
| Art | External files: `art/<key>-emblem.webp`, `art/<key>-portrait.webp`, `art/units/*.webp` | 7 webp sprites inlined as base64 (54 KB); all card scenes are generated SVG | 45 webp inlined as base64 (456 KB): 24 faction emblems, 11 unit sprites, 10 animation frames |
| Artifact-only APIs | `claude.use("downloads")` for the Markdown export | `claude.use('downloads')`, `claude.hot.snapshot/ready` (hot reload) | `claude.use('downloads')` |
| Links to each other | Hard-coded claude.ai URL to the Council | — | Hard-coded claude.ai URL for its own `#display` TV mode |
| Fonts | Google Fonts: Oxanium, Barlow, JetBrains Mono | Oxanium, Barlow, JetBrains Mono | Barlow Semi Condensed, Oxanium |

Things worth knowing:

* **Three faction naming schemes.** Ledger uses full names, the Council uses long slugs, the Arbiter uses short keys (`vuil`, `naaz`, `sardakk`). `shared/factions.js` maps all of them to one id.
* **The unit sprites are the same files in all three tools** (byte-identical), so they now live once in `assets/units/`.
* **Export fallbacks differ.** The Council and Arbiter already fall back to a normal browser download when `claude.use` is missing. The Ledger falls back to the clipboard, then a copy-from-text box, so it needs a real download added.
* The Arbiter's TV mode uses `BroadcastChannel` + a `storage` event. That only works between windows **on the same device** and keeps working on a normal site.
* The Ledger already records every agenda VP source by hand (`SOURCES`: censure, mutiny-for/against, seed, rider, leak) and has an Incentive Program button. Integration (b) fills those in for you; it doesn't need a new scoring model.
* The Council's record already stores per-seat votes and outcomes (`record[].detail.seats`), so Mutiny's "who voted For" can be computed, not re-asked.
* Moving to a new web address means **the new site starts with empty storage**. Games saved in the claude.ai artifacts don't carry over automatically (see §5).

## 2. Repo layout

```
/                         GitHub Pages serves this folder as-is (no build step)
├─ index.html             Shell: top bar (Ledger · Council · Arbiter), setup wizard, notice
├─ ledger/                Ledger module (index.html, scenes.js, scenes.css)
├─ council/               Council Chamber module
├─ arbiter/               Battle Arbiter module (also /arbiter/#display for the TV)
├─ shared/
│  ├─ factions.js         Canonical faction ids, names, legacy keys, colours, art paths   ✅ written
│  ├─ table.js            Shared table state: read/write/subscribe                       (next)
│  ├─ bus.js              Cross-module events (BroadcastChannel + storage fallback)      (next)
│  ├─ download.js         Plain browser download helper                                  (next)
│  └─ shell.css           Top bar + shared tokens only, so module styles stay separate
├─ assets/
│  ├─ units/              11 unit sprites (CC BY, see NOTICE.md)
│  └─ factions/
│     ├─ emblems/         24 small emblems the Ledger uses
│     ├─ emblems-px/      24 larger pixel-art emblems the Arbiter uses
│     └─ portraits-REVIEW/ 24 portraits — official FFG art, must not be published (ART-AUDIT.md)
├─ docs/                  ARCHITECTURE.md, ART-AUDIT.md
├─ _import/               Untouched originals from the artifacts
├─ NOTICE.md  README.md  .nojekyll
```

**Why one folder per tool, hosted inside the shell.** The shell loads each module in its own same-origin
`<iframe>` and only hides/shows them when you switch tabs. That gives you:

* Isolation: each module keeps its own CSS, globals and code. A bug in one can't break the others.
* "Return to the same turn" for free: the Ledger stays alive (timers, open step) while the Arbiter is on screen.
* Shared storage: same origin, so all modules see the same `localStorage`.
* Each module still opens on its own at `/ledger/`, `/council/`, `/arbiter/` (phones, the TV display).

Plain HTML/JS, no framework and no build, matching how the tools are written now. GitHub Pages
publishes straight from the `main` branch.

## 3. Shared state

One namespace, `ti4gm:`. The shared part is deliberately small; each tool keeps owning its own data.

```js
// localStorage "ti4gm:table"  — the single source of truth for who is playing
{
  v: 1,
  gameId: "g-2026-11-26-x7k",      // new id per game; module state is tagged with it
  createdAt: 1795740000000,
  goal: 10,                         // VP to win
  players: [                        // seat order = clockwise
    { id: "p1", name: "Ben", faction: "sol", color: "blue" },
    { id: "p2", name: "Alex", faction: "hacan", color: "yellow" }
  ],
  speaker: "p1"
}

// Module state, one key each, same shapes the tools use today plus a gameId tag:
"ti4gm:ledger"   // was ti4-objective-ledger-v1
"ti4gm:council"  // was galactic-council-chamber-v1
"ti4gm:arbiter"  // was ti4-arbiter-game-v1 (+ cfg, tvzoom as sub-fields)
```

Rules:

* **Players are referenced by `id` everywhere.** Each module gets a small adapter that turns the table
  into its own shape (Ledger: `faction` → full name; Council: seats + speaker index; Arbiter: roster keyed by faction).
* **Who writes what.** Only the setup wizard (and the Ledger's Edit/Setup) writes `ti4gm:table`. The
  Politics primary and the Council write `speaker`. Everything else is module-private.
* **Live updates.** `shared/table.js` fires a `table` event on change (via `bus.js`); open modules re-render.
* **New game** = new `gameId`. A module whose saved state has an old `gameId` starts fresh for the new game.

### Cross-module events (`shared/bus.js`)

```js
{ type: "council:open",     round: 4 }                                      // Ledger → Council
{ type: "council:resolved", ref: "c12", agenda: "mutiny", outcome: "for",
  vp: [{ pid: "p2", pts: 1, src: "mutiny-for" }, { pid: "p5", pts: 1, src: "mutiny-for" }] }
{ type: "council:law",      ref: "c14", agenda: "political-censure", holder: "p3", active: true }
{ type: "arbiter:open",     attacker: "p1", defender: "p4", system: "", returnTo: { round: 4, turn: "t37" } }
{ type: "arbiter:result",   ref: "b9", winner: "p1", attacker: "p1", defender: "p4", summary: "…" }
```

* `ref` makes each event idempotent: the Ledger stores it on the resulting entry, so a replayed
  event can't double-score, and Undo removes it cleanly.
* VP changes from the Council show as a short "Apply?" card in the Ledger, not silently. Players stay in control.
* Seed of an Empire is sent as an outcome only; the Ledger knows the scores, so it works out the
  leader/last place (and asks if there's a tie).

## 4. Integration plan (your priority order)

**(a) Shared players and factions.** Setup wizard writes `ti4gm:table`; all three modules read it.
Remove the separate player pickers in the Council and Arbiter (or turn them into "edit table").

**(b) Agenda phase → Council → Ledger score.**
1. Ledger agenda phase gets "Open the Council Chamber" (replaces the claude.ai link). It switches the shell tab.
2. When the Council resolves an agenda it emits `council:resolved` / `council:law`.
3. Ledger turns them into its existing `extras` (Mutiny, Seed, Censure, Imperial Rider), opens its
   leak picker (Classified Document Leaks) or reveal flow (Incentive Program). Censure is removed if the law is repealed.

**(c) Tactical action → Arbiter → back.**
1. In the tactical-action guide, the space/ground combat steps get "Resolve in the Battle Arbiter" with an attacker/defender picker (active player preselected).
2. The Arbiter opens with both factions loaded, using its saved techs/upgrades for those factions.
3. On finish it emits `arbiter:result`; the shell returns to the Ledger on the same step and the turn timer keeps running.
4. Optional extra: if the result could satisfy a combat secret (e.g. destroy a flagship), the Ledger offers to score it.

## 5. Port checklist per module

* Replace `art/...` and inlined base64 images with `../assets/...` paths (Arbiter shrinks from 827 KB to ~370 KB).
* Drop `claude.use("downloads")` and `claude.hot`; use `shared/download.js` and a plain `start()`.
* Replace hard-coded claude.ai URLs with relative routes.
* Rename storage keys to `ti4gm:*`, read players from the table adapter.
* Add a one-time **Import game** box: paste the JSON from the old artifact's Edit/Export panel to carry a game in progress over.

## 6. Hosting

GitHub Pages, deploy from branch `main`, folder `/`. `.nojekyll` is present so `_import/` and other
underscore folders are served. Free, HTTPS, URL `https://<user>.github.io/<repo>/`. All paths in the
site are relative so the repo name doesn't matter. Netlify/Cloudflare Pages can serve the same folder unchanged.

Later (optional): live sync across devices with Supabase or Firebase by mirroring `ti4gm:*` keys to a
room code. Nothing in this design blocks that.

## 7. Test matrix

Desktop 1440 px, tablet 820 px, phone 390 px, for each module and for the tab switch, setup wizard,
agenda hand-off and combat hand-off.
