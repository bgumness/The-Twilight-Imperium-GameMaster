# TI4 GameMaster

A free companion website for Twilight Imperium 4th Edition + Prophecy of Kings, made by fans.
Open it and the opening screen explains everything. Three tools share one table setup:

- **Ledger** — objectives, VP track, round console, player clocks, game log.
- **Council Chamber** — agenda reveals with card art, voting and a laws/outcomes record.
- **Battle Arbiter** — automatic combat resolution in place of rolling dice, with a TV display mode.

There's also a TV table screen and a season record of finished games.

Everything runs in your browser. Your game is saved on your device; there are no accounts and no server.

## Run it locally

Any static server works, for example:

```
npx serve .
# or
python -m http.server 8000
```

Then open http://localhost:8000 (opening `index.html` straight from disk blocks some browser features).

## Project

- `docs/ARCHITECTURE.md` — how the tools fit together and the shared game state.
- `docs/ART-AUDIT.md` — art that must be replaced before going public.
- `_import/` — the original tool code, kept unchanged for reference.

See [NOTICE.md](NOTICE.md) for the fan-content notice and credits.
