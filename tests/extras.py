"""Season undo, regular players, Keleres tech choice, Esc, old direct links."""
import asyncio, json
from playwright.async_api import async_playwright
from _env import launch, new_context
async def run():
    async with async_playwright() as p:
        b = await launch(p); ctx = await new_context(b, viewport={"width": 1440, "height": 900}); errs = []
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
        await pg.goto("http://localhost:8765/#game"); await pg.wait_for_timeout(2500)
        L = next(f for f in pg.frames if f.url.endswith('/ledger/'))
        click = lambda sel: L.evaluate("s=>{const e=document.querySelector(s); if(!e) throw new Error('missing '+s); e.click()}", sel)
        async def wizard(names, facs, keleres_pick=None):
            await click('[data-act="wizard"]'); await click(f'[data-w="n"][data-v="{len(names)}"]'); await click('[data-w="next"]')
            for i, (n, f) in enumerate(zip(names, facs)):
                if n: await L.fill(f'[data-w="name"][data-i="{i}"]', n)
                if i == 0: await click('[data-w="pickfor"][data-i="0"]')
                await click(f'[data-w="fac"][data-v="{f}"]')
            await click('[data-w="next"]'); await click('[data-w="speaker"][data-i="0"]'); await click('[data-w="next"]')
            if keleres_pick is not None:
                opts = await L.evaluate("()=>[...document.querySelectorAll('.wz-trow')].map(r=>r.innerText.replace(/\\n/g,' | '))")
                print("keleres row:", [o for o in opts if 'Keleres' in o])
                for t in keleres_pick: await click(f'[data-w="tch"][data-i="{len(names)-1}"][data-t="{t}"]')
            await click('[data-w="next"]'); await click('[data-w="start"]'); await pg.wait_for_timeout(900); await pg.keyboard.press("Escape")
        # 1. Keleres chooses from what the others start with
        await wizard(["Ben", "Alex", "Kel"], ["Barony of Letnev", "Xxcha Kingdom", "Council Keleres"], ["Plasma Scoring", "Graviton Laser System"])
        print("1 Keleres profile:", await pg.evaluate("()=>{const t=TI4.table.read(); const k=t.players.find(p=>p.faction==='keleres'); return TI4.profiles.get(k.id)}"))
        # 2. win, then undo: the season entry goes away
        await click('[data-act="award"]'); await pg.wait_for_timeout(200)
        for _ in range(10):
            await L.evaluate("()=>{document.querySelector('[data-act=award]').click()}"); await pg.wait_for_timeout(120)
            await L.evaluate("()=>[...document.querySelectorAll('#awSrc [data-src]')].find(b=>/\\+1 VP/.test(b.textContent) && !/Custodians/.test(b.textContent)).click()"); await pg.wait_for_timeout(80)
            await L.evaluate("()=>document.querySelector('#awBody [data-aw-p]').click()"); await L.evaluate("()=>{const g=document.getElementById('awGo'); if(!g.disabled) g.click()}"); await pg.wait_for_timeout(200)
            if await L.evaluate("()=>!document.getElementById('victory')?.hidden || document.querySelector('.vc-head') && getComputedStyle(document.querySelector('.vc-head').closest('[id]')).display!=='none'"): break
        season = lambda: pg.evaluate("()=>(JSON.parse(localStorage.getItem('ti4gm:seasons'))||[]).length")
        print("2 after reaching 10 VP, season games:", await season())
        await L.evaluate("()=>document.getElementById('vcBack')?.click()"); await pg.wait_for_timeout(300)
        await L.evaluate("()=>document.querySelector('[data-act=undo]').click()"); await pg.wait_for_timeout(500)
        print("  after Undo, season games:", await season())
        # 3. regulars: next setup offers the names and the same table
        await click('[data-act="wizard"]'); await click('[data-w="next"]'); await pg.wait_for_timeout(200)
        print("3 regulars offered:", await L.evaluate("()=>[...document.querySelectorAll('.wz-reg .chip')].map(c=>c.textContent)"))
        await click('[data-w="lasttable"]'); await pg.wait_for_timeout(200)
        print("  same table fills:", await L.evaluate("()=>[...document.querySelectorAll('[data-w=\"name\"]')].map(i=>i.value)"))
        await pg.keyboard.press("Escape"); await L.evaluate("()=>{const d=document.getElementById('wizard'); if(d && !d.hidden) d.querySelector('[data-close], .x, [data-w=close]')?.click()}")
        # 4. Esc closes the Council (but not while one of its own windows is open)
        await L.evaluate("()=>document.querySelector('[data-act=council]').click()"); await pg.wait_for_timeout(2000)
        C = next(f for f in pg.frames if f.url.endswith('/council/'))
        await C.evaluate("()=>document.getElementById('btnPlayers').click()"); await pg.wait_for_timeout(300)
        await C.press('body', 'Escape'); await pg.wait_for_timeout(700)
        on = lambda: pg.evaluate("()=>document.querySelector('.sheet[data-tool=council]').classList.contains('on')")
        print("4 Esc with Delegates open -> Council still up:", await on())
        await C.press('body', 'Escape'); await pg.wait_for_timeout(900)
        print("  Esc again -> Council up:", await on())
        # 5. an old direct link
        q = await ctx.new_page(); await q.goto("http://localhost:8765/ledger/"); await q.wait_for_timeout(2000)
        print("5 old /ledger/ link lands on:", q.url)
        q2 = await ctx.new_page(); await q2.goto("http://localhost:8765/arbiter/#display"); await q2.wait_for_timeout(1500)
        print("  battle display link stays:", q2.url)
        print("ERRORS:", errs); await b.close()
asyncio.run(run())
