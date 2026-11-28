import asyncio
from playwright.async_api import async_playwright
from _env import launch, new_context, new_page
async def run():
    async with async_playwright() as p:
        b=await launch(p); ctx=await new_context(b, viewport={"width":390,"height":844},is_mobile=True,has_touch=True); errs=[]
        pg=await ctx.new_page(); pg.on("console",lambda m: m.type=="error" and "404" not in m.text and errs.append(m.text[:150]))
        await pg.goto("about:blank"); await pg.goto("http://localhost:8765/"); await pg.wait_for_timeout(2800)
        fr=lambda n: next(f for f in pg.frames if f.url.endswith('/'+n+'/'))
        where=lambda: pg.evaluate("()=>{const on=[...document.querySelectorAll('.sheet.on')].map(s=>s.dataset.tool); return (on[0]||'ledger')+' '+location.hash}")
        async def back(): await pg.go_back(); await pg.wait_for_timeout(900); return pg.url.startswith('http') and await where() or pg.url
        print("start:", await where())
        await fr('home').evaluate("()=>document.querySelector('[data-go=continue]').click()"); await pg.wait_for_timeout(900); print("continue:", await where())
        await fr('ledger').evaluate("()=>document.querySelector('[data-act=council]').click()"); await pg.wait_for_timeout(1500); print("council button:", await where())
        print("Back:", await back())
        print("Back:", await back())
        await fr('home').evaluate("()=>document.querySelector('[data-go=continue]').click()"); await pg.wait_for_timeout(900); print("continue again:", await where())
        await fr('ledger').evaluate("()=>document.querySelector('[data-act=battle]').click()"); await pg.wait_for_timeout(1800); print("battle button:", await where())
        await fr('arbiter').evaluate("()=>document.querySelector('#gmPill button').click()"); await pg.wait_for_timeout(1100); print("arbiter 'Back to the game':", await where())
        await fr('ledger').evaluate("()=>document.querySelector('[data-act=home]').click()"); await pg.wait_for_timeout(1100); print("Home button:", await where())
        print("Back (should leave the site):", await back())
        # opened straight at #game
        q=await ctx.new_page(); await q.goto("about:blank"); await q.goto("http://localhost:8765/#game"); await q.wait_for_timeout(2500)
        L=next(f for f in q.frames if f.url.endswith('/ledger/'))
        await L.evaluate("()=>document.querySelector('[data-act=council]').click()"); await q.wait_for_timeout(1500)
        await q.go_back(); await q.wait_for_timeout(900); print("#game link, council then Back:", q.url, await q.evaluate("()=>[...document.querySelectorAll('.sheet.on')].map(s=>s.dataset.tool)"))
        await L.evaluate("()=>document.querySelector('[data-act=home]').click()"); await q.wait_for_timeout(1100)
        print("then Home button:", q.url, await q.evaluate("()=>[...document.querySelectorAll('.sheet.on')].map(s=>s.dataset.tool)"))
        print("errors:", errs); await b.close()
asyncio.run(run())
