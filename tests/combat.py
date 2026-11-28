import asyncio
from playwright.async_api import async_playwright
from _env import launch, new_context, new_page
async def run():
    async with async_playwright() as p:
        b=await launch(p); pg=await new_page(b, viewport={"width":1440,"height":900}); errs=[]
        pg.on("console",lambda m: m.type=="error" and "404" not in m.text and errs.append(m.text[:200]))
        await pg.goto("http://localhost:8765/"); await pg.wait_for_timeout(2500)
        L=next(f for f in pg.frames if f.url.endswith('/ledger/'))
        await L.evaluate("""()=>{[...document.querySelectorAll('#rcMain button')].find(b=>/TACTICAL ACTION/i.test(b.textContent)).click()}"""); await pg.wait_for_timeout(400)
        await L.evaluate("""()=>{[...document.querySelectorAll('[data-g="gstep"]')].find(b=>/Space combat/i.test(b.title)).click()}"""); await pg.wait_for_timeout(400)
        await L.evaluate("()=>document.querySelector('[data-g=\"arb\"]').click()"); await pg.wait_for_timeout(2500)
        A=next(f for f in pg.frames if f.url.endswith('/arbiter/'))
        print("sheet up:", await pg.evaluate("()=>document.querySelector('.sheet[data-tool=arbiter]').classList.contains('on')"), "| pill:", await A.evaluate("()=>document.getElementById('gmPill').textContent"), "| step:", await A.evaluate("()=>document.querySelector('.wstep.on, [aria-current=step]')?.textContent || ''"))
        await A.evaluate("()=>window.__gm.battleDone({winner:'D',rounds:3},'The Federation of Sol holds the system')"); await pg.wait_for_timeout(500)
        await A.evaluate("()=>document.querySelector('#gmPill button').click()"); await pg.wait_for_timeout(1000)
        print("back:", not await pg.evaluate("()=>document.querySelector('.sheet[data-tool=arbiter]').classList.contains('on')"), "| log:", await L.evaluate("()=>JSON.parse(localStorage.getItem('ti4-objective-ledger-v1')).log.slice(-1)[0].t"), "| step:", await L.evaluate("()=>document.querySelector('.g-steps .on')?.textContent"))
        print("ERRORS:", errs); await b.close()
asyncio.run(run())
