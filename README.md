# Collide

Allows the user to generate ideas from the collisions of paired keywords.

Ten keywords are collected, shuffled, and matched into five pairs. Each pair is
shown in turn, and the idea entered for it is written to a timestamped file.

## Requirements

- Python 3.8 or later
- No third-party dependencies — only `datetime`, `random`, and `os` from the standard library

## Usage

Run from the repository root:

```
python3 src/collide.py
```

The program is interactive and reads exactly 15 lines: 10 keywords, then one
idea for each of the 5 resulting pairs. It exits with an `EOFError` traceback if
fewer are supplied.

Running from the repository root matters — the output directory is resolved
relative to the current working directory, so starting the program from `src/`
creates a second `src/ideas/` directory instead of using the tracked one.

Ideas are written to `ideas/ideas-<timestamp>.txt`, one line per pair, formatted
as `['keyword', 'keyword']: idea`.

## Example

Ten keywords are requested one at a time:

```
Enter 1st keyword: Enter 2nd keyword: Enter 3rd keyword: ... Enter 10th keyword:
```

Once all ten have been entered they are shuffled and paired, and each pair is
presented for an idea:

```
Enter an idea based off of these keywords: ['fishing', 'branching choices']
Enter an idea: Enter an idea based off of these keywords: ['world modification', 'mining']
Enter an idea: Enter an idea based off of these keywords: ['social mobility', 'community']
Enter an idea: Enter an idea based off of these keywords: ['antagonist', 'complex relationships']
Enter an idea: Enter an idea based off of these keywords: ['interaction', 'exploration']
Enter an idea:
```

Because the prompts are written without trailing newlines, they run together on
one line when input is piped in rather than typed.

The resulting `ideas/ideas-<timestamp>.txt` holds one line per pair, as recorded
in [`ideas/example.txt`](ideas/example.txt):

```
['complex relationships', 'fishing']: The innkeeper should purchase food from fishermen and sell it at an upcharge.
['mining', 'world modification']: Make changes in the mine persistent.
```

Keywords are shuffled before pairing, so the pairs differ from run to run even
when the same keywords are entered in the same order.

## Tests

The tests use `unittest` from the standard library. Run them from the
repository root:

```
python3 -m unittest discover -s tests
```

Every prompt is patched, so no test waits on real input.

The same two commands — `py_compile` over both modules and the test suite — are
run on every push to `main` and on every pull request by
[`.github/workflows/tests.yml`](.github/workflows/tests.yml), against Python 3.8
and 3.13.

## License

See [LICENSE](LICENSE).
