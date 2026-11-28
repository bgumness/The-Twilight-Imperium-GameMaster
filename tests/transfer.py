import asyncio, json, sys
from playwright.async_api import async_playwright
from _env import launch, new_context, new_page
W,H = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv)>2 else (1440,900)
async def run():
    async with async_playwright() as p:
        b=await launch(p)
        ctx=await new_context(b, viewport={"width":W,"height":H}, is_mobile=W<600, has_touch=W<600)
        pg=await ctx.new_page(); errs=[]
        pg.on("console",lambda m: m.type=="error" and "404" not in m.text and errs.append(m.text[:200]))
        await pg.goto("http://localhost:8765/"); await pg.wait_for_timeout(2500)
        L=next(f for f in pg.frames if f.url.endswith('/ledger/'))
        click=lambda sel: L.evaluate("s=>{const e=document.querySelector(s); if(!e) throw new Error('missing '+s); e.click()}", sel)
        fr=lambda n: next(f for f in pg.frames if f.url.endswith('/'+n+'/'))
        async def back(n): await fr(n).evaluate("()=>document.querySelector('#gmPill button').click()"); await pg.wait_for_timeout(800)
        # 1. open both tools on the sample game first (Ben's order)
        await click('[data-act="council"]'); await pg.wait_for_timeout(2200); await back('council')
        await click('[data-act="battle"]'); await pg.wait_for_timeout(2200); await back('arbiter')
        # 2. set up a real game
        await click('[data-act="wizard"]'); await pg.wait_for_timeout(300)
        await click('[data-w="n"][data-v="4"]'); await click('[data-w="next"]'); await pg.wait_for_timeout(200)
        for i,(n,f) in enumerate(zip(["Ben","Alex","Jordan","Sam"],["Argent Flight","Barony of Letnev","Mahact Gene-Sorcerers","Xxcha Kingdom"])):
            await L.fill(f'[data-w="name"][data-i="{i}"]', n)
            if i==0: await click('[data-w="pickfor"][data-i="0"]')
            await click(f'[data-w="fac"][data-v="{f}"]')
        await click('[data-w="next"]'); await click('[data-w="speaker"][data-i="1"]'); await click('[data-w="next"]'); await pg.wait_for_timeout(200)
        await click('[data-w="tch"][data-i="0"][data-t="Plasma Scoring"]'); await click('[data-w="tch"][data-i="0"][data-t="Neural Motivator"]')
        await click('[data-w="next"]'); await click('[data-w="start"]'); await pg.wait_for_timeout(1000); await pg.keyboard.press("Escape")
        # 3. Arbiter shows the NEW players without touching anything
        await click('[data-act="battle"]'); await pg.wait_for_timeout(1500); A=fr('arbiter')
        vis=await A.evaluate("()=>document.body.innerText.match(/THIS GAME[\\s\\S]{0,90}/i)?.[0]?.replace(/\\n/g,' ')")
        print("3 arbiter shows:", vis)
        await A.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Game & factions/i.test(b.textContent)).click()"); await pg.wait_for_timeout(500)
        print("  game & factions:", await A.evaluate("()=>document.getElementById('gamebody').innerText.slice(0,160).replace(/\\n/g,' | ')"))
        await A.evaluate("()=>document.getElementById('g-cancel').click()"); await pg.wait_for_timeout(300)
        # 4. change a setting inside the Arbiter -> shared
        fast=await A.evaluate("()=>{const el=document.getElementById('ui-fast')||document.getElementById('ui-fast2'); if(!el) return 'no toggle on this screen'; el.click(); return el.checked}")
        await pg.wait_for_timeout(300)
        print("4 arbiter fast toggled ->", fast, "| shared:", await pg.evaluate("()=>TI4.options.read().fast"))
        await back('arbiter')
        # 5. change motion in the Ledger menu -> Council live
        await click('[data-act="council"]'); await pg.wait_for_timeout(2000); C=fr('council'); await back('council')
        before=await C.evaluate("()=>document.body.classList.contains('still')")
        await click('[data-act="menu"]'); await pg.wait_for_timeout(300); await click('[data-opt="motion"]'); await pg.wait_for_timeout(400)
        after=await C.evaluate("()=>document.body.classList.contains('still')")
        print("5 council still before/after menu toggle:", before, after, "| menu chips:", await L.evaluate("()=>[...document.querySelectorAll('#mnOpts .chip')].map(c=>c.textContent+':'+c.getAttribute('aria-pressed'))"))
        await pg.keyboard.press("Escape"); await L.evaluate("()=>document.querySelectorAll('.overlay:not([hidden]),[id=menu]').forEach(d=>{d.hidden=true})")
        # 6. Council: Delegates locked; make Sam speaker; tick an ability
        await click('[data-act="council"]'); await pg.wait_for_timeout(1500)
        await C.evaluate("()=>document.getElementById('btnPlayers').click()"); await pg.wait_for_timeout(300)
        print("6 delegates add-seat visible:", await C.evaluate("()=>getComputedStyle(document.getElementById('plForm')).display"), "| heading:", await C.evaluate("()=>document.getElementById('plH').textContent"))
        await pg.screenshot(path=f"tr-{W}-delegates.png")
        await C.evaluate("()=>document.querySelector('[data-sspk=\"3\"]').click()"); await pg.wait_for_timeout(300)
        await C.evaluate("()=>{const c=document.querySelector('[data-sf=\"0|pi\"]'); c.click(); }"); await pg.wait_for_timeout(300)
        await C.evaluate("()=>document.querySelector('[data-close=\"players\"]').click()"); await back('council'); await pg.wait_for_timeout(500)
        lg=await L.evaluate("()=>{const s=JSON.parse(localStorage.getItem('ti4-objective-ledger-v1')); return [s.players.find(p=>p.id===s.g.speaker).name, s.log.slice(-1)[0].t]}")
        print("  ledger speaker now:", lg, "| Ben votes:", await pg.evaluate("()=>{const t=TI4.table.read(); return TI4.profiles.get(t.players[0].id).votes}"))
        # 7. bundle round trip
        await click('[data-act="menu"]'); await pg.wait_for_timeout(300)
        await L.evaluate("()=>document.getElementById('mnCopy').click()"); await pg.wait_for_timeout(300)
        bundle=await L.evaluate("()=>document.getElementById('mnJson').value")
        bj=json.loads(bundle); print("7 bundle keys:", sorted(k for k in bj if bj[k] is not None))
        await L.evaluate("()=>document.getElementById('mnSample').click()"); await pg.wait_for_timeout(800)
        await click('[data-act="menu"]'); await pg.wait_for_timeout(300)
        await L.evaluate("b=>{document.getElementById('mnJson').value=b; document.getElementById('mnLoad').click()}", bundle); await pg.wait_for_timeout(900)
        print("  after load:", await L.evaluate("()=>[document.getElementById('mnJsonHint').textContent, S_names=JSON.parse(localStorage.getItem('ti4-objective-ledger-v1')).players.map(p=>p.name).join(',')]"),
              "| council seats:", await pg.evaluate("()=>JSON.parse(localStorage.getItem('galactic-council-chamber-v1')).seats.map(s=>s.name+(s.flags.pi?'(PI)':'')).join(',')"))
        # 8. a plain game from the old Claude Ledger (no game id, no extras)
        old=json.loads(bundle)['ledger']; [old.pop(k,None) for k in ('gid','done','battles')]
        await L.evaluate("b=>{document.getElementById('mnJson').value=b; document.getElementById('mnLoad').click()}", json.dumps(old)); await pg.wait_for_timeout(900)
        print("8 old-format load:", await L.evaluate("()=>document.getElementById('mnJsonHint').textContent"), "| profiles seeded:", await pg.evaluate("()=>Object.values(TI4.profiles.all()).map(p=>p.techs.join('+')||'-').join(' / ')"))
        print("ERRORS:", errs); await b.close()
asyncio.run(run())
