# Pair programming practice — Python data manipulation & testing

A mock of a timed pair-programming interview: an existing skeleton, a set of
tasks, standard library only. Open it in a browser-based VS Code to mimic the
hosted environment.

## Launch in the browser

1. On GitHub: **Code → Codespaces → Create codespace on main**.
2. Wait for VS Code to load in the browser (Python extension installs automatically).
3. Open `TASKS.md` and start with Task 1.

## Run

```bash
python -m unittest -v       # run all tests
python src/main.py          # end-to-end report (works once tasks are done)
```

You can also use the **Testing** panel (flask icon) in the VS Code sidebar.

## Layout

```
data/            transactions.csv (deliberately messy), fx_rates.json
src/main.py      entry point that prints a report
src/sales/       models.py (done), loader.py and analysis.py (your tasks)
tests/           unittest suites, partly written
TASKS.md         the brief
```

## Simulating the real thing

- Set a 60–90 minute timer.
- Talk out loud as you work, as if a navigator is listening. Explain what you
  are about to do *before* you type it.
- No AI tools. Docs are fine: https://docs.python.org/3/library/
- Reset to a clean start any time: `git checkout main && git reset --hard origin/main`
- Practise on a branch so `main` stays clean: `git checkout -b attempt-1`
- **Check your answers afterwards** (not during!): the `solutions` branch has a
  reference implementation, a full test suite and `SOLUTIONS.md` with talking
  points. Compare with `git diff attempt-1 origin/solutions -- src tests`, or
  run the reference tests against your code with
  `git checkout origin/solutions -- tests && python -m unittest -v`.
