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
├─ index.html             Shell: the Ledger full-screen; Council and Arbiter slide up over it. About/notice   ✅
├─ home/                  Opening screen: explains the site, game in progress, season stats, table screen, options, saved games, credits   ✅
├─ table/                 TV table screen (read-only; follows the game live on the same device)   ✅
├─ ledger/                Ledger module (index.html, scenes.js, scenes.css)   ✅ ported: shared art, real download
├─ council/               Council Chamber module   ✅ ported: players from the table, results to the Ledger
├─ arbiter/               Battle Arbiter module (also /arbiter/#display for the TV)   ✅ ported: roster from the table, battles from/to the Ledger
├─ shared/
│  ├─ factions.js         Canonical faction ids, names, legacy keys, colours, art paths   ✅ written
│  ├─ table.js            Shared table, outbox (results between modules), pending requests ✅
│  └─ bus.js              Cross-module messages (BroadcastChannel + storage fallback)        ✅
├─ assets/
│  ├─ units/              11 unit sprites (CC BY, see NOTICE.md)
│  └─ factions/
│     ├─ emblems-px/      24 faction symbols (from the Battle Arbiter), used by every module
│     └─ portraits/       24 portraits — official FFG art, © credit shown beside each (ART-AUDIT.md)
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

## 8. Built (2026-11-26): one game flow

* **Shared players.** The Ledger's setup is the single source. Every Ledger save publishes `ti4gm:table`
  (game id, players with canonical faction ids and colours, speaker, round, phase). The Council rebuilds its
  seats from it (keeping per-seat ability flags) and the Arbiter rebuilds its roster (keeping each faction's
  techs/upgrades). A new game id resets the Council record and the Arbiter roster.
* **Agenda phase.** The Ledger's agenda phase has "Open the Council Chamber". When the Council resolves
  Mutiny, Seed of an Empire, Political Censure, Classified Document Leaks or Incentive Program, or an
  Imperial Rider pays out, it writes an outbox item. The Ledger lists these under "From the Council
  Chamber" with Record/Reveal and Dismiss. Record opens the Ledger's own points dialog pre-filled (Mutiny
  voters from the vote tally, Seed winner from the current scores, the censured player, the leaked secret).
  A repealed Political Censure offers to remove the point. Results are tied to the Ledger's Undo.
* **Combat.** The Space combat and Ground combat steps of a tactical action show the Battle Arbiter: pick
  the defender, the shell switches to the Arbiter with both factions and their saved techs loaded, at the
  System step. When the battle ends the result goes to the Ledger's log, and "Back to the Ledger" returns
  to the same step with the turn timer still running.
* **Shell (revised).** No top bar. The Ledger fills the screen; the Council and Arbiter slide up over it
  as sheets and stay alive when hidden. The Council rises when the agenda phase starts and sinks back after
  the second agenda; the Arbiter rises from a combat step. Both can also be opened from the Ledger's
  Council and Battle buttons, and each has a "Back to the game" button.
* **One setup.** The Ledger's wizard now also covers the other tools: a Table options panel (battle sound,
  fast battle animations, auto-advance rule tips, animated agenda reveals → `ti4gm:options`) and a Starting
  technologies list filled from each faction sheet (`TI4.START` in shared/factions.js; Argent picks 2,
  Winnu picks 1).
* **Shared tech + abilities record.** `ti4gm:profiles` holds one record per player: Arbiter tech keys,
  unit upgrades, Arbiter flags, Council voting abilities, starting techs by name. Setup seeds it (e.g.
  Letnev → Antimass + Plasma Scoring in the Arbiter; Mahact → Predictive Intelligence in the Council).
  The Arbiter writes it on every roster save and reads it on sync; the Council writes its seat abilities
  on save and reads them on sync.

Known gaps:
* The modules keep their original storage keys (`ti4-objective-ledger-v1`, `galactic-council-chamber-v1`,
  `ti4-arbiter-*`). Renaming buys nothing now that Copy game / Load pasted game carry everything.
* Mutiny voters need the Council's vote tally; if the outcome is recorded without running the tally, the
  Ledger asks who voted For.
* Headers now match (seal + label + title). Deeper visual unification of the module bodies is still open.

## 9. Room left for later

* **Table screen (TV).** A `#table` route in the shell for a big display: score track, current phase and
  speaker from `ti4gm:table`, the Council's reveal, and the Arbiter's existing battle display. Everything it
  needs is already broadcast on the bus, so it can be a read-only page that just listens.
* **Season stats.** On "End game" the Ledger will append a summary to `ti4gm:seasons` (date, players,
  factions, winner, VP by source, rounds, time); the Arbiter already keeps per-faction battle stats
  (`GAME.stats`) and the Council keeps every agenda. A Stats page reads all three. Export/import as JSON
  so a season survives clearing the browser.
* **One name.** The shell shows "GameMaster" as a placeholder; one constant to change.

## 10. Settings travel (2026-11-26, revised)

* Players, factions, colours and seating are owned by the Ledger's setup. The Arbiter's Game & factions
  screen and the Council's Delegates panel show them read-only inside the site; whatever screen the Arbiter
  is on refreshes when they change (never mid-battle).
* Table options (`ti4gm:options`) can be changed in the setup wizard, the Ledger's Game setup menu, the
  Arbiter (sound, fast animations, rule tips) or the Council (motion), and every open tool applies them live.
* Speaker: any change in the Council (Politics Rider, Public Execution, Make speaker) becomes a
  `council:speaker` outbox item that the Ledger applies and logs.
* A faction changed or a player added in Game setup gets that faction's starting techs in `ti4gm:profiles`.
* Copy game copies a bundle `{gm:1, ledger, council, arbiter, profiles, options, outbox}`; Load pasted game
  accepts the bundle or a plain Ledger game from the old Claude artifact (the Council and Arbiter then start
  fresh for it). The shell closes the Council and Arbiter before the data is written so they can't save over it.

## 11. Opening screen, season stats, table screen (2026-11-27)

* **Opening screen (`home/`).** Shown when the site opens (the Ledger loads behind it). Explains the three
  tools, shows the game in progress with Continue / New game (or Start a game / Explore a sample game), and
  holds what doesn't belong on the gameplay screen: season stats, the TV table screen and battle display,
  table options, saved games, credits. The Ledger's Home button returns to it. `#game` opens straight into
  play. Requests to the Ledger go through `TI4.pending.set('ledger', {act})` so they work even while the
  Ledger is still loading.
* **Season stats.** When the Victory or Game over screen appears (not Standings), the Ledger writes a summary
  to `ti4gm:seasons` (one entry per game id; replaced if the game is ended again; sample games and games where
  nobody scored are skipped): players with VP by type and turn time, winners, rounds, minutes, battles from the
  Arbiter, agendas and laws from the Council. The opening screen shows totals, player standings (players are
  matched across games by name), Hall of champions, factions and recurring laws, and can save/load a season file.
* **Table screen (`table/`).** Reads `ti4gm:board` (published by the Ledger on every save: round, phase,
  active player, speaker, VP by type, revealed objectives with scorers, last battle) and `ti4gm:laws`
  (published by the Council). Updates live over the bus with a 5-second fallback poll; asks the browser to
  keep the screen awake; scales the score lanes to fit up to 8 players.

## 12. Review fixes (2026-11-27)

* **Council Keleres** is mapped in `shared/factions.js` (Ledger "Council Keleres", Arbiter `keleres`, Council
  `council-keleres`) with an original symbol; no portrait. Its starting technologies show a note instead of a list.
* **Two tabs or windows** of the same game: the Ledger, Council and Arbiter listen for `storage` events on their
  own keys and reload from another tab's save instead of overwriting it (the Arbiter never mid-battle). The Ledger
  shows "Updated from another window".
* **Back button**: the shell keeps a small history stack (opening screen → game → Council/Arbiter). Going deeper
  pushes an entry; the on-screen ways back use `history.back()` when the entry below is the site's own, so the
  browser/phone Back button and the buttons agree. Opening at `#game` never steps back off the site.
* **Fonts** are served from `shared/fonts/` (OFL). No page loads anything from another site.
* The Seed of an Empire tie note no longer states a ruling.
