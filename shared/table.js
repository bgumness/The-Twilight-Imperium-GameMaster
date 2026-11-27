/* Shared game state for the GameMaster site. Needs shared/bus.js and shared/factions.js first.

   ti4gm:table   who is playing — the one record every module reads
   ti4gm:outbox  results one module hands to another (agenda outcomes, battle results)
   ti4gm:pending a request waiting for a module to open (e.g. "resolve this battle")

   The Ledger's setup writes the table. The Council and Arbiter read it.
   Each module still keeps its own detailed state under its own key. */
(function (root) {
  const TI4 = root.TI4 = root.TI4 || {};
  const K = { table: 'ti4gm:table', outbox: 'ti4gm:outbox', pending: 'ti4gm:pending' };
  const get = k => { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } };
  const put = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } };

  TI4.newGid = () => 'g' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);

  TI4.table = {
    /* { v:1, gid, goal, round, players:[{id,name,faction,color}], speaker } or null */
    read() { const t = get(K.table); return t && t.v === 1 && Array.isArray(t.players) ? t : null; },
    write(t) {
      const next = Object.assign({ v: 1 }, t);
      const prev = get(K.table);
      if (prev && JSON.stringify(prev) === JSON.stringify(next)) return false;
      put(K.table, next);
      TI4.emit('table', { gid: next.gid });
      return true;
    },
    player(id) { const t = this.read(); return t ? t.players.find(p => p.id === id) || null : null; },
    /* Match a typed or elected name ("Ben", "Federation of Sol", "The Federation of Sol") to a player id. */
    findByName(name) {
      const t = this.read(); if (!t || !name) return null;
      const n = String(name).trim().toLowerCase().replace(/^the\s+/, '');
      const hit = t.players.find(p => p.name.trim().toLowerCase() === n) ||
        t.players.find(p => { const f = TI4.faction && TI4.faction(p.faction); return f && f.name.toLowerCase().replace(/^the\s+/, '') === n; });
      return hit ? hit.id : null;
    }
  };

  TI4.outbox = {
    push(ev) {
      const t = TI4.table.read();
      const item = Object.assign({ ref: 'r' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6), gid: t ? t.gid : null, ts: Date.now() }, ev);
      const list = (get(K.outbox) || []).concat([item]).slice(-300);
      put(K.outbox, list);
      TI4.emit('outbox', { ref: item.ref, kind: item.kind });
      return item;
    },
    list(gid) { return (get(K.outbox) || []).filter(x => !gid || x.gid === gid); }
  };

  TI4.pending = {
    set(tool, req) { const all = get(K.pending) || {}; all[tool] = Object.assign({ ts: Date.now() }, req); put(K.pending, all); TI4.emit('pending', { tool }); },
    peek(tool) { const all = get(K.pending) || {}; return all[tool] || null; },
    clear(tool) { const all = get(K.pending) || {}; delete all[tool]; put(K.pending, all); }
  };
})(window);
