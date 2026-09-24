# Collide

Allows the user to generate ideas from the collisions of paired keywords.

Ten keywords are collected, shuffled, and matched into five pairs. Each pair is
shown in turn, and the idea entered for it is written to a timestamped file.

## Requirements

- Python 3.8 or later
- No third-party dependencies — only the standard library (the vendored usage-reporting client in `src/trace_client.py` included)

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

[`.github/workflows/tests.yml`](.github/workflows/tests.yml) runs the same
commands on every push to `main` and on every pull request, against Python 3.8
and 3.13: `py_compile` over both modules, the test suite, and one full run of
the program with a 15-line fixture on stdin.

## Usage reporting

Usage reporting is on by default: Collide sends its name (`Collide`), its version and the events
`startup` (when the program starts) and `ideas-written` (when a session's ideas have been saved)
to [trace](https://github.com/Stephenson-Software/trace) at `https://trace.danielstephenson.dev`.
Nothing about you, your machine, your IP address, the keywords or the ideas is sent. The report
is made from a background thread, never blocks the program, and is dropped silently if the
service is unreachable.

The first launch writes a `settings.json` at the repository root and prints a one-line notice.
To turn reporting off, any one of these is enough:

- `"usage_reporting": {"enabled": false}` in `settings.json`:

  ```json
  {
    "usage_reporting": {
      "enabled": false
    }
  }
  ```

- the environment variable `TRACE_USAGE_REPORTING=off` (also `false`, `0`, `no`), which turns off
  every program that reports to trace
- the environment variable `DO_NOT_TRACK=1` (see [consoledonottrack.com](https://consoledonottrack.com))

The environment variables win over `settings.json`. The `endpoint` and `key` entries in the same
block select where reports go and the key they are sent with. The client is `src/trace_client.py`,
vendored from [trace-client-python](https://github.com/Stephenson-Software/trace-client-python);
the settings handling is in `src/usage_reporting.py`. Only a command-line run reports; the test
suite's direct `main()` calls do not, and the CI run sets `TRACE_USAGE_REPORTING=off`.

Details: https://github.com/Stephenson-Software/trace#usage-reporting

## License

See [LICENSE](LICENSE).
