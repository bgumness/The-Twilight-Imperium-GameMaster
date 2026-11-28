# Browser tests

End-to-end checks of the whole site in a real browser, at desktop and phone widths: setup wizard,
settings carrying across the three tools, agenda and combat hand-offs, opening screen, season record,
table screen, Keleres, two tabs, the Back button, self-hosted fonts, and offline use with safe updates.

```
pip install playwright
python -m playwright install chromium
python tests/run_all.py
```

Screenshots land in `test-output/` (ignored by git). Each script prints what it checked and ends with
`ERRORS: []` when the pages logged no errors.
