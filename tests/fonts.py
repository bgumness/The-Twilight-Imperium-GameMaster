import asyncio
from playwright.async_api import async_playwright
from _env import launch, new_context, new_page
async def run():
    async with async_playwright() as p:
        b=await launch(p); pg=await new_page(b, viewport={"width":1440,"height":900}); ext=[]
        pg.on("request", lambda r: (not r.url.startswith("http://localhost") and not r.url.startswith("data:") and not r.url.startswith("about:")) and ext.append(r.url))
        await pg.goto("http://localhost:8765/"); await pg.wait_for_timeout(2500)
        for n in ['home','ledger']:
            f=next(x for x in pg.frames if x.url.endswith('/'+n+'/'))
            print(n, await f.evaluate("async()=>{await document.fonts.ready; return [...document.fonts].filter(x=>x.status==='loaded').map(x=>x.family.replace(/\"/g,'')+' '+x.weight).sort()}"))
        L=next(x for x in pg.frames if x.url.endswith('/ledger/')); await L.evaluate("()=>document.querySelector('[data-act=battle]').click()"); await pg.wait_for_timeout(2200)
        A=next(x for x in pg.frames if x.url.endswith('/arbiter/'))
        print('arbiter', await A.evaluate("async()=>{await document.fonts.ready; return [...document.fonts].filter(x=>x.status==='loaded').map(x=>x.family.replace(/\"/g,'')+' '+x.weight).sort()}"))
        print("requests to other sites:", ext)
        await b.close()
asyncio.run(run())
