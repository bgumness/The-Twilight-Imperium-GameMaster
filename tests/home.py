import asyncio, json, sys
from playwright.async_api import async_playwright
from _env import launch, new_context, new_page
W,H = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv)>2 else (1440,900)
async def run():
    async with async_playwright() as p:
        b=await launch(p)
        ctx=await new_context(b, viewport={"width":W,"height":H}, is_mobile=W<600, has_touch=W<600)
        pg=await ctx.new_page(); errs=[]
        pg.on("console",lambda m: m.type=="error" and "404" not in m.text and errs.append("shell: "+m.text[:200]))
        await pg.goto("http://localhost:8765/"); await pg.wait_for_timeout(3000)
        fr=lambda n: next(f for f in pg.frames if f.url.endswith('/'+n+'/'))
        Hm=fr('home'); L=fr('ledger')
        print("1 home on:", await pg.evaluate("()=>document.querySelector('.sheet[data-tool=home]').classList.contains('on')"), "| card:", await Hm.evaluate("()=>document.getElementById('current').innerText.replace(/\\n/g,' ')"), "| buttons:", await Hm.evaluate("()=>[...document.querySelectorAll('#cta .btn')].map(b=>b.textContent)"))
        await pg.screenshot(path=f"home-{W}-hero.png")
        await Hm.evaluate("()=>document.getElementById('flow').scrollIntoView()"); await pg.wait_for_timeout(500); await pg.screenshot(path=f"home-{W}-flow.png")
        await Hm.evaluate("()=>document.getElementById('season').scrollIntoView()"); await pg.wait_for_timeout(400); await pg.screenshot(path=f"home-{W}-season-empty.png")
        # Continue -> Ledger, Home button -> back
        await Hm.evaluate("()=>document.querySelector('[data-go=continue]').click()"); await pg.wait_for_timeout(900)
        print("2 after continue home on:", await pg.evaluate("()=>document.querySelector('.sheet[data-tool=home]').classList.contains('on')"), "| hash:", await pg.evaluate("()=>location.hash"))
        await L.evaluate("()=>document.querySelector('[data-act=home]').click()"); await pg.wait_for_timeout(900)
        print("  home button -> home on:", await pg.evaluate("()=>document.querySelector('.sheet[data-tool=home]').classList.contains('on')"))
        # New game from home opens the wizard
        await Hm.evaluate("()=>document.querySelector('[data-go=wizard]').click()"); await pg.wait_for_timeout(900)
        print("3 wizard open:", await L.evaluate("()=>!!document.querySelector('[data-w=\"n\"]')"))
        click=lambda sel: L.evaluate("s=>{const e=document.querySelector(s); if(!e) throw new Error('missing '+s); e.click()}", sel)
        await click('[data-w="n"][data-v="3"]'); await click('[data-w="next"]')
        for i,(n,f) in enumerate(zip(["Ben","Alex","Jordan"],["Federation of Sol","Emirates of Hacan","Naalu Collective"])):
            await L.fill(f'[data-w="name"][data-i="{i}"]', n)
            if i==0: await click('[data-w="pickfor"][data-i="0"]')
            await click(f'[data-w="fac"][data-v="{f}"]')
        await click('[data-w="next"]'); await click('[data-w="speaker"][data-i="0"]'); await click('[data-w="next"]'); await click('[data-w="next"]'); await click('[data-w="start"]'); await pg.wait_for_timeout(900); await pg.keyboard.press("Escape")
        # give Ben 2 points through the Ledger's own award dialog
        await click('[data-act="award"]'); await pg.wait_for_timeout(300)
        await L.evaluate("()=>{const c=[...document.querySelectorAll('#awSrc [data-src]')].find(b=>/\\+1 VP/.test(b.textContent)); c.click();}"); await pg.wait_for_timeout(200)
        await L.evaluate("()=>document.querySelector('#awBody [data-aw-p]').click()"); await pg.wait_for_timeout(200)
        await L.evaluate("()=>{const g=document.getElementById('awGo'); if(!g.disabled) g.click()}"); await pg.wait_for_timeout(400)
        # table screen in a second window
        T=await ctx.new_page(); await T.goto("http://localhost:8765/table/"); await T.wait_for_timeout(1500)
        print("4 table:", await T.evaluate("()=>[document.getElementById('rn').textContent, document.getElementById('ph').textContent, [...document.querySelectorAll('.lane')].map(l=>l.querySelector('b').textContent+':'+l.querySelector('.vp').firstChild.textContent).join(' '), document.getElementById('spk').innerText.replace(/\\n/g,' ')]"))
        await click('[data-g="goto"][data-ph="action"]'); await pg.wait_for_timeout(1200)
        print("  table live after phase change:", await T.evaluate("()=>document.getElementById('ph').textContent"))
        await T.screenshot(path=f"table-{W}.png")
        # end the game -> season
        await click('[data-act="menu"]'); await pg.wait_for_timeout(300); await L.evaluate("()=>document.getElementById('mnEnd').click()"); await pg.wait_for_timeout(1200)
        seas=await pg.evaluate("()=>JSON.parse(localStorage.getItem('ti4gm:seasons'))")
        print("5 season recorded:", len(seas or []), seas and [(x['name'],x['faction'],x['total']) for x in seas[-1]['players']], "winners:", seas and seas[-1]['winners'])
        # add two synthetic past games so the dashboard has something to show
        await pg.evaluate("""()=>{const s=JSON.parse(localStorage.getItem('ti4gm:seasons'))||[];
          const mk=(gid,d,ws,pl,bat)=>({gid,date:d,rounds:6,goal:10,minutes:290,winners:ws,reached:true,players:pl,battles:bat,agendas:[{round:2,id:'political-censure',pill:'law'},{round:3,id:'minister-of-war',pill:'law'}],laws:[]});
          s.push(mk('gA','2026-11-08T03:00:00Z',['a1'],[{id:'a1',name:'Alex',faction:'hacan',color:'yellow',pub:6,sec:3,oth:1,total:10},{id:'a2',name:'Ben',faction:'letnev',color:'red',pub:5,sec:2,oth:1,total:8},{id:'a3',name:'Jordan',faction:'xxcha',color:'green',pub:4,sec:2,oth:0,total:6}],[{round:3,att:'a2',def:'a3',winner:'a2'},{round:4,att:'a1',def:'a2',winner:'a2'}]));
          s.push(mk('gB','2026-11-15T03:00:00Z',['b2'],[{id:'b1',name:'Alex',faction:'mahact',color:'purple',pub:5,sec:2,oth:1,total:8},{id:'b2',name:'Ben',faction:'sol',color:'blue',pub:6,sec:3,oth:1,total:10},{id:'b3',name:'Jordan',faction:'naalu',color:'green',pub:6,sec:1,oth:0,total:7}],[{round:2,att:'b1',def:'b2',winner:'b1'}]));
          localStorage.setItem('ti4gm:seasons',JSON.stringify(s)); TI4.emit('season',{});}""")
        await pg.keyboard.press("Escape"); await L.evaluate("()=>document.getElementById('vcBack')?.click()")
        await L.evaluate("()=>document.querySelector('[data-act=home]').click()"); await pg.wait_for_timeout(1200)
        await Hm.evaluate("()=>document.getElementById('season').scrollIntoView()"); await pg.wait_for_timeout(500)
        print("6 season kpis:", await Hm.evaluate("()=>[...document.querySelectorAll('.kpi')].map(k=>k.innerText.replace(/\\n/g,' '))"))
        print("  standings:", await Hm.evaluate("()=>[...document.querySelectorAll('#seasonBody tbody')][0].innerText.replace(/\\t/g,' ').split('\\n').slice(0,4)"))
        await pg.screenshot(path=f"home-{W}-season.png")
        # full-page shot of home
        await Hm.evaluate("()=>scrollTo(0,0)")
        print("ERRORS:", errs); await b.close()
asyncio.run(run())
