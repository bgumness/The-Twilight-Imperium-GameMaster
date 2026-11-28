import asyncio, json
from playwright.async_api import async_playwright
from _env import launch, new_context, new_page
EVIL='<img src=x onerror="window.__xss=(window.__xss||0)+1">Ben'
async def run():
    async with async_playwright() as p:
        b=await launch(p)
        ctx=await new_context(b, viewport={"width":1440,"height":900})
        pg=await ctx.new_page(); errs=[]; bytes_=[0]; reqs=[]
        pg.on("console",lambda m: m.type=="error" and errs.append(m.text[:160]))
        pg.on("response", lambda r: reqs.append(r.url))
        await pg.goto("http://localhost:8765/#game"); await pg.wait_for_timeout(2500)
        L=next(f for f in pg.frames if f.url.endswith('/ledger/'))
        click=lambda sel: L.evaluate("s=>{const e=document.querySelector(s); if(!e) throw new Error('missing '+s); e.click()}", sel)
        await click('[data-act="wizard"]'); await click('[data-w="n"][data-v="3"]'); await click('[data-w="next"]')
        for i,(n,f) in enumerate(zip([EVIL,"Alex","Kel"],["Federation of Sol","Emirates of Hacan","Council Keleres"])):
            await L.fill(f'[data-w="name"][data-i="{i}"]', n)
            if i==0: await click('[data-w="pickfor"][data-i="0"]')
            await click(f'[data-w="fac"][data-v="{f}"]')
        await click('[data-w="next"]'); await click('[data-w="speaker"][data-i="0"]'); await click('[data-w="next"]'); await click('[data-w="next"]'); await click('[data-w="start"]'); await pg.wait_for_timeout(900); await pg.keyboard.press("Escape")
        t=await pg.evaluate("()=>TI4.table.read().players.map(p=>[p.name.slice(0,8),p.faction])"); print("table:",t)
        await click('[data-act="council"]'); await pg.wait_for_timeout(2200)
        C=next(f for f in pg.frames if f.url.endswith('/council/'))
        print("council seats:", await C.evaluate("()=>JSON.parse(localStorage.getItem('galactic-council-chamber-v1')).seats.map(s=>[s.name.slice(0,8),s.fac])"))
        await C.evaluate("()=>document.querySelector('#gmPill button').click()"); await pg.wait_for_timeout(600)
        await click('[data-act="battle"]'); await pg.wait_for_timeout(2200)
        A=next(f for f in pg.frames if f.url.endswith('/arbiter/'))
        print("arbiter roster:", await A.evaluate("()=>JSON.parse(localStorage.getItem('ti4-arbiter-game-v1')).players.map(p=>[p.name.slice(0,8),p.fac])"))
        await A.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Game & factions/i.test(b.textContent)).click()"); await pg.wait_for_timeout(400)
        await A.evaluate("()=>document.querySelector('#gmPill button').click()"); await pg.wait_for_timeout(500)
        # combat request against Keleres
        await L.evaluate("""()=>{[...document.querySelectorAll('[data-g="goto"]')].find(b=>b.dataset.ph==='action').click()}"""); await pg.wait_for_timeout(300)
        await L.evaluate("""()=>{const t=[...document.querySelectorAll('#rcMain button')].find(b=>/TACTICAL ACTION/i.test(b.textContent)); t&&t.click()}"""); await pg.wait_for_timeout(300)
        await L.evaluate("""()=>{const c=[...document.querySelectorAll('[data-g="gstep"]')].find(b=>/Space combat/i.test(b.title)); c&&c.click()}"""); await pg.wait_for_timeout(300)
        chips=await L.evaluate("()=>[...document.querySelectorAll('[data-g=\"arb\"]')].map(b=>b.dataset.p+':'+b.textContent.trim().slice(-6))"); print("arb chips:",chips)
        kel=[c for c in chips if c.endswith('Kel')]
        if kel: 
            await L.evaluate("p=>document.querySelector(`[data-g=\"arb\"][data-p=\"${p}\"]`).click()", kel[0].split(':')[0]); await pg.wait_for_timeout(1800)
            print("arbiter after Keleres request:", await A.evaluate("()=>[document.getElementById('gmPill')?.textContent, JSON.parse(localStorage.getItem('ti4-arbiter-cfg-v1')).D.fac]"))
            await A.evaluate("()=>document.querySelector('#gmPill button').click()"); await pg.wait_for_timeout(500)
        # home + table with the evil name and keleres
        await L.evaluate("()=>document.querySelector('[data-act=home]').click()"); await pg.wait_for_timeout(1500)
        Hm=next(f for f in pg.frames if f.url.endswith('/home/'))
        T=await ctx.new_page(); await T.goto("http://localhost:8765/table/"); await T.wait_for_timeout(1500)
        xss=[await f.evaluate("()=>window.__xss||0") for f in pg.frames] + [await T.evaluate("()=>window.__xss||0")]
        print("script ran from a player name in frames:", xss)
        broken=await Hm.evaluate("()=>[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src.split('/').slice(-2).join('/'))")
        print("home broken images:", broken, "| table broken:", await T.evaluate("()=>[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src.split('/').slice(-2).join('/'))"))
        sizes=await pg.evaluate("()=>Object.keys(localStorage).map(k=>[k,localStorage.getItem(k).length]).sort((a,b)=>b[1]-a[1])")
        print("storage:", sizes)
        print("third-party hosts:", sorted({r.split('/')[2] for r in reqs if 'localhost' not in r}))
        print("errors:", [e for e in errs if '404' not in e][:6])
        await b.close()
asyncio.run(run())
