import asyncio, json, sys
from playwright.async_api import async_playwright
from _env import launch, new_context, new_page
W,H = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv)>2 else (1440,900)
tag = f"{W}"
PRE = "pre" in sys.argv
async def run():
    async with async_playwright() as p:
        b=await launch(p)
        ctx=await new_context(b, viewport={"width":W,"height":H}, is_mobile=W<600, has_touch=W<600)
        pg=await ctx.new_page(); errs=[]
        pg.on("console",lambda m: m.type=="error" and "404" not in m.text and errs.append(m.text[:200]))
        await pg.goto("http://localhost:8765/"); await pg.wait_for_timeout(2500)
        L=next(f for f in pg.frames if f.url.endswith('/ledger/'))
        await pg.screenshot(path=f"ng-{tag}-0-base.png")
        click=lambda sel: L.evaluate("s=>{const e=document.querySelector(s); if(!e) throw new Error('missing '+s); e.click()}", sel)
        if PRE:
            await click('[data-act="council"]'); await pg.wait_for_timeout(2200)
            C0=next(f for f in pg.frames if f.url.endswith('/council/')); await C0.evaluate("()=>document.querySelector('#gmPill button').click()"); await pg.wait_for_timeout(700)
            await click('[data-act="battle"]'); await pg.wait_for_timeout(2200)
            A0=next(f for f in pg.frames if f.url.endswith('/arbiter/')); await A0.evaluate("()=>document.querySelector('#gmPill button').click()"); await pg.wait_for_timeout(700)
        await click('[data-act="wizard"]'); await pg.wait_for_timeout(400)
        await click('[data-w="n"][data-v="4"]'); await click('[data-w="opt"][data-k="fast"]'); await click('[data-w="opt"][data-k="motion"]')
        await pg.wait_for_timeout(200); await pg.screenshot(path=f"ng-{tag}-1-game.png")
        await click('[data-w="next"]'); await pg.wait_for_timeout(300)
        names=["Ben","Alex","Jordan","Sam"]; facs=["Argent Flight","Barony of Letnev","Mahact Gene-Sorcerers","Xxcha Kingdom"]
        for i,(n,f) in enumerate(zip(names,facs)):
            await L.fill(f'[data-w="name"][data-i="{i}"]', n)
            if i==0: await click(f'[data-w="pickfor"][data-i="{i}"]'); await pg.wait_for_timeout(100)
            await click(f'[data-w="fac"][data-v="{f}"]'); await pg.wait_for_timeout(100)
        await click('[data-w="next"]'); await pg.wait_for_timeout(300)
        await click('[data-w="speaker"][data-i="1"]'); await click('[data-w="next"]'); await pg.wait_for_timeout(300)
        # starting techs: Argent chooses Plasma Scoring + Sarween Tools
        await click('[data-w="tch"][data-i="0"][data-t="Plasma Scoring"]'); await click('[data-w="tch"][data-i="0"][data-t="Sarween Tools"]')
        await pg.wait_for_timeout(300)
        rows=await L.evaluate("()=>[...document.querySelectorAll('.wz-trow')].map(r=>r.innerText.replace(/\\n/g,' | '))")
        print("tech step:", rows)
        await L.evaluate("()=>document.querySelector('.wz-tech').scrollIntoView()")
        await pg.screenshot(path=f"ng-{tag}-2-techs.png")
        await click('[data-w="next"]'); await pg.wait_for_timeout(300)
        await click('[data-w="start"]'); await pg.wait_for_timeout(1200)
        await L.evaluate("()=>document.querySelectorAll('dialog[open], .dlg:not([hidden])').forEach(d=>{try{d.close&&d.close()}catch(e){}})")
        await pg.keyboard.press("Escape"); await pg.wait_for_timeout(300)
        prof=await pg.evaluate("()=>{const t=TI4.table.read(), p=TI4.profiles.all(); return t.players.map(x=>[x.name,x.faction,p[x.id]&&p[x.id].techs,p[x.id]&&p[x.id].votes])}")
        print("profiles:", prof); print("options:", await pg.evaluate("()=>TI4.options.read()"))
        # Council slides in from the Council button
        await click('[data-act="council"]'); await pg.wait_for_timeout(2200)
        print("council sheet on:", await pg.evaluate("()=>document.querySelector('.sheet[data-tool=council]')?.classList.contains('on')"))
        C=next(f for f in pg.frames if f.url.endswith('/council/'))
        print("council VISIBLE:", await C.evaluate("()=>document.body.innerText.slice(0,0)+[...document.querySelectorAll('#players:not([hidden]) input')].map(i=>i.value).join(',')"), "| setup open:", await C.evaluate("()=>{const d=document.querySelector('#players'); return d? !d.hidden : 'n/a'}"))
        print("council seats:", await C.evaluate("()=>JSON.parse(localStorage.getItem('galactic-council-chamber-v1')).seats.map(s=>[s.name,s.fac,s.flags])"),
              "still:", await C.evaluate("()=>document.body.classList.contains('still')"))
        await pg.screenshot(path=f"ng-{tag}-3-council.png")
        await C.evaluate("()=>document.querySelector('#gmPill button').click()"); await pg.wait_for_timeout(900)
        print("after back: sheet on:", await pg.evaluate("()=>document.querySelector('.sheet[data-tool=council]').classList.contains('on')"))
        # Battle button -> Arbiter with shared techs
        await click('[data-act="battle"]'); await pg.wait_for_timeout(2500)
        A=next(f for f in pg.frames if f.url.endswith('/arbiter/'))
        print("arbiter VISIBLE chips:", await A.evaluate("()=>[...document.querySelectorAll('.rosterchips button, .gchip, [data-roster]')].map(b=>b.textContent.trim()).slice(0,8)"), "| visible text:", await A.evaluate("()=>document.body.innerText.match(/THIS GAME[\\s\\S]{0,160}/i)?.[0]?.replace(/\\n/g,' ')"))
        print("arbiter roster:", await A.evaluate("()=>JSON.parse(localStorage.getItem('ti4-arbiter-game-v1')).players.map(p=>[p.name,p.fac,p.techs])"),
              "ui:", await A.evaluate("()=>{const c=JSON.parse(localStorage.getItem('ti4-arbiter-cfg-v1')).ui;return [c.fast,c.quick,c.sound]}"))
        await pg.screenshot(path=f"ng-{tag}-4-arbiter.png")
        await A.evaluate("()=>document.querySelector('#gmPill button').click()"); await pg.wait_for_timeout(900)
        # Agenda: custodians, then entering the agenda phase brings the Council up by itself
        await click('[data-g="goto"][data-ph="agenda"]'); await pg.wait_for_timeout(500)
        await click('[data-g="custodians"]'); await pg.wait_for_timeout(500)
        await click('[data-g="goto"][data-ph="status"]'); await pg.wait_for_timeout(400)
        await click('[data-g="goto"][data-ph="agenda"]'); await pg.wait_for_timeout(1800)
        print("auto council on agenda:", await pg.evaluate("()=>document.querySelector('.sheet[data-tool=council]').classList.contains('on')"))
        # resolve 2 agendas -> back to the game automatically
        async def play(card,out):
            await C.click('#btnReveal'); await pg.wait_for_timeout(300); await C.click(f'[data-card="{card}"]'); await pg.wait_for_timeout(900)
            await C.click(f'#rvPanel [data-out="{out}"]'); await pg.wait_for_timeout(500)
            await C.evaluate("()=>{const p=document.getElementById('procl'); if(p && !p.hidden) p.click()}"); await pg.wait_for_timeout(1500)
        await play('seed-of-an-empire','for')
        print("after 1st agenda sheet on:", await pg.evaluate("()=>document.querySelector('.sheet[data-tool=council]').classList.contains('on')"))
        await play('incentive-program','against')
        print("after 2nd agenda sheet on:", await pg.evaluate("()=>document.querySelector('.sheet[data-tool=council]').classList.contains('on')"))
        print("ledger inbox:", await L.evaluate("()=>[...document.querySelectorAll('.gm-row span')].map(s=>s.textContent)"))
        await pg.screenshot(path=f"ng-{tag}-5-back.png")
        print("ERRORS:", errs); await b.close()
asyncio.run(run())
