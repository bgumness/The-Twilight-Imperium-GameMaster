/* Cross-module messages for the GameMaster site.
   Every page on the site (shell and the three modules) loads this file.
   Messages go to every other open page of the site on this device through a
   BroadcastChannel, and to listeners in the same page. Nothing leaves the device. */
(function (root) {
  const TI4 = root.TI4 = root.TI4 || {};
  const subs = {};
  let ch = null;
  try { ch = new BroadcastChannel('ti4gm'); } catch (e) { ch = null; }

  function deliver(msg) {
    [].concat(subs[msg.type] || [], subs['*'] || []).forEach(fn => {
      try { fn(msg); } catch (e) { console.error('[ti4gm bus]', msg.type, e); }
    });
  }
  if (ch) ch.onmessage = e => deliver(e.data);
  else root.addEventListener('storage', e => {
    if (e.key === 'ti4gm:bus' && e.newValue) { try { deliver(JSON.parse(e.newValue)); } catch (_) {} }
  });

  TI4.on = (type, fn) => { (subs[type] = subs[type] || []).push(fn); return () => { subs[type] = subs[type].filter(f => f !== fn); }; };
  TI4.emit = (type, data) => {
    const msg = Object.assign({ type, ts: Date.now(), from: location.pathname }, data || {});
    if (ch) { try { ch.postMessage(msg); } catch (e) {} }
    else { try { localStorage.setItem('ti4gm:bus', JSON.stringify(msg)); } catch (e) {} }
    deliver(msg);
    return msg;
  };

  /* Is this page running inside the shell (index.html) or opened on its own? */
  TI4.inShell = (() => { try { return root.parent !== root && !!root.parent.TI4_SHELL; } catch (e) { return false; } })();

  /* Switch to another module. Inside the shell this flips the tab (the current module
     stays alive); opened on its own it navigates to that module's page. */
  TI4.open = (tool, extra) => {
    if (TI4.inShell) TI4.emit('shell:open', Object.assign({ tool }, extra || {}));
    else location.href = '../' + tool + '/';
  };
})(window);
