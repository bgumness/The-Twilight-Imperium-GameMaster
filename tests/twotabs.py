import asyncio
from playwright.async_api import async_playwright
from _env import launch, new_context, new_page
async def run():
    async with async_playwright() as p:
        b=await launch(p); ctx=await new_context(b, viewport={"width":1440,"height":900}); errs=[]
        A=await ctx.new_page(); await A.goto("http://localhost:8765/#game"); await A.wait_for_timeout(2500)
        B=await ctx.new_page(); await B.goto("http://localhost:8765/#game"); await B.wait_for_timeout(2500)
        for pg in (A,B): pg.on("console",lambda m: m.type=="error" and "404" not in m.text and errs.append(m.text[:150]))
        LA=next(f for f in A.frames if f.url.endswith('/ledger/')); LB=next(f for f in B.frames if f.url.endswith('/ledger/'))
        tot=lambda: A.evaluate("()=>{const s=JSON.parse(localStorage.getItem('ti4-objective-ledger-v1')); return s?s.log.length+' | last: '+s.log.slice(-2).map(x=>x.t).join(' / '):'unsaved'}")
        await LA.evaluate("""()=>{[...document.querySelectorAll('[data-g="goto"]')].find(b=>b.dataset.ph==='strategy').click()}"""); await A.wait_for_timeout(600)
        before=await tot()
        await LA.evaluate("()=>document.querySelector('[data-act=award]').click()"); await A.wait_for_timeout(200)
        await LA.evaluate("()=>[...document.querySelectorAll('#awSrc [data-src]')].find(b=>/\\+1 VP/.test(b.textContent)).click()"); await A.wait_for_timeout(100)
        await LA.evaluate("()=>document.querySelector('#awBody [data-aw-p]').click()"); await LA.evaluate("()=>document.getElementById('awGo').click()"); await A.wait_for_timeout(500)
        print("tab A awarded a point: extras", before, "->", await tot())
        print("tab B notice shown:", await LB.evaluate("()=>document.getElementById('syncNote')?.style.opacity"))
        await LB.evaluate("""()=>{[...document.querySelectorAll('[data-g="goto"]')].find(b=>b.dataset.ph==='status').click()}"""); await B.wait_for_timeout(500)
        print("after tab B acts: extras", await tot(), "| phase", await A.evaluate("()=>JSON.parse(localStorage.getItem('ti4-objective-ledger-v1')).g.phase"))
        # Council in two tabs
        await LA.evaluate("()=>document.querySelector('[data-act=council]').click()"); await LB.evaluate("()=>document.querySelector('[data-act=council]').click()"); await A.wait_for_timeout(2200)
        CA=next(f for f in A.frames if f.url.endswith('/council/')); CB=next(f for f in B.frames if f.url.endswith('/council/'))
        await CA.click('#btnReveal'); await A.wait_for_timeout(300); await CA.click('[data-card="seed-of-an-empire"]'); await A.wait_for_timeout(800)
        await CA.click('#rvPanel [data-out="for"]'); await A.wait_for_timeout(600)
        await CA.evaluate("()=>{const p=document.getElementById('procl'); if(p && !p.hidden) p.click()}"); await A.wait_for_timeout(500)
        await CB.evaluate("()=>document.getElementById('btnMotion').click()"); await B.wait_for_timeout(500)
        print("council record after tab B saves:", await A.evaluate("()=>JSON.parse(localStorage.getItem('galactic-council-chamber-v1')).record.map(r=>r.id)"))
        print("errors:", errs); await b.close()
asyncio.run(run())
