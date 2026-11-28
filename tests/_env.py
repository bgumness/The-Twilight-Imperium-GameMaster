"""Shared setup for the browser tests (Playwright for Python).

The site must be served at http://localhost:8765 (run_all.py does that). Set CHROME to use an installed
Chrome instead of Playwright's Chromium. Screenshots go into the current folder (run_all.py uses test-output/)."""
import os

TEST_FLAG = "try { localStorage.setItem('ti4gm:test', '1'); } catch (e) {}"

async def launch(p):
    exe = os.environ.get('CHROME')
    return await p.chromium.launch(**({'executable_path': exe} if exe else {}))

async def new_context(b, **kw):
    ctx = await b.new_context(**kw)
    await ctx.add_init_script(TEST_FLAG)      # switches on the Arbiter's test hook
    return ctx

async def new_page(b, **kw):
    ctx = await new_context(b, **kw)
    return await ctx.new_page()
