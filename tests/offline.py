"""Offline copy and safe updates: load once, go offline, everything still opens; a new version waits for 'Update now'."""
import asyncio, os, re, subprocess, sys
from playwright.async_api import async_playwright
from _env import launch, new_context
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
async def run():
    async with async_playwright() as p:
        b = await launch(p); ctx = await new_context(b, viewport={"width": 1440, "height": 900}); errs = []
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
        await pg.goto("http://localhost:8765/"); await pg.wait_for_timeout(1500)
        await pg.evaluate("async()=>{ await navigator.serviceWorker.ready; }")
        await pg.reload(); await pg.wait_for_timeout(2500)         # now controlled by the service worker
        n = await pg.evaluate("async()=>{const k=(await caches.keys()).find(x=>x.startsWith('gamemaster-')); return [k, (await (await caches.open(k)).keys()).length]}")
        print("1 cached:", n, "| controlled:", await pg.evaluate("()=>!!navigator.serviceWorker.controller"))
        await ctx.set_offline(True)
        await pg.reload(); await pg.wait_for_timeout(2500)
        fr = lambda name: next(f for f in pg.frames if f.url.endswith('/' + name + '/'))
        print("2 offline reload, home shows:", await fr('home').evaluate("()=>document.querySelector('h1').textContent"))
        await fr('home').evaluate("()=>document.querySelector('[data-go]').click()"); await pg.wait_for_timeout(1200)
        L = fr('ledger')
        await L.evaluate("()=>document.querySelector('[data-act=council]').click()"); await pg.wait_for_timeout(2000)
        print("3 offline, Council opens:", await fr('council').evaluate("()=>document.title"))
        await fr('council').evaluate("()=>document.querySelector('#gmPill button').click()"); await pg.wait_for_timeout(900)
        await L.evaluate("()=>document.querySelector('[data-act=battle]').click()"); await pg.wait_for_timeout(2000)
        A = fr('arbiter'); print("  offline, Arbiter opens:", await A.evaluate("()=>document.title"), "| broken images:", await A.evaluate("()=>[...document.images].filter(i=>i.complete&&!i.naturalWidth).length"))
        T = await ctx.new_page(); await T.goto("http://localhost:8765/table/"); await T.wait_for_timeout(1500)
        print("  offline, table screen:", await T.evaluate("()=>document.title"))
        await T.close(); await ctx.set_offline(False)
        # publish a "new version": the notice must appear, and nothing switches until Update now
        old = await pg.evaluate("()=>window.TI4_VERSION")
        sw = open(os.path.join(ROOT, 'sw.js'), encoding='utf-8').read()
        open(os.path.join(ROOT, 'sw.js'), 'w', encoding='utf-8').write(re.sub(r"const VERSION = '[^']+'", "const VERSION = 'test-next'", sw))
        try:
            await pg.evaluate("async()=>{ const r=await navigator.serviceWorker.getRegistration(); await r.update(); }")
            await pg.wait_for_timeout(4000)
            print("4 update notice shown:", await pg.evaluate("()=>!document.getElementById('upd').hidden"), "| still old version until tapped:", await pg.evaluate("async()=>(await caches.keys()).includes('gamemaster-test-next') && !!navigator.serviceWorker.controller"))
            await pg.evaluate("()=>document.getElementById('updNow').click()"); await pg.wait_for_timeout(3500)
            print("5 after Update now, active cache:", await pg.evaluate("async()=>(await caches.keys()).filter(k=>k.startsWith('gamemaster-'))"))
        finally:
            open(os.path.join(ROOT, 'sw.js'), 'w', encoding='utf-8').write(sw)
        print("ERRORS:", errs); await b.close()
asyncio.run(run())
