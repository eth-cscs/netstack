# AGENTS.md

Guidance for coding agents working in this repository.

## What this repository is

Netstack holds reference documentation and tools for describing and diagnosing the network stack of applications on the Alps system at CSCS.

| Path | Contents |
|---|---|
| `docs/` | The documentation, built with Material for MkDocs. |
| `docs/contributing.md` | The writing guide. Authoritative for everything under `docs/`. |
| `bin/` | Three standalone `uv` scripts — `system-stack`, `user-stack`, `spack-db` — and the modules they share. |
| `mkdocs.yml` | Site configuration and the navigation tree. |
| `site/` | Generated output. Never edit it, and never commit it. |

## Before editing anything under `docs/`

**Read `docs/contributing.md` first, in full.**
It is the style guide for this documentation, and it is specific enough that guessing from the surrounding text is not a substitute for reading it.

The rules that are easiest to break by accident:

1. Write one sentence per line, and turn off automatic line wrapping. Never hard-wrap a paragraph at a column limit.
2. Link to other pages with references, `[libfabric][ref-pkg-libfabric]`, and not with relative paths. Reference names follow the convention set out in the guide.
3. Every page carries its page reference immediately above its title. Add a section reference only when something links to that section.
4. Give every code block a lexer and, where it makes sense, a `title=`. Use `console` for a session with output and `$` prompts, and `bash` for commands meant to be copied.
5. Follow the Voice section: state facts rather than framing them, keep bold for definitions and warnings, and prefer a full stop to a dash.
6. Use admonitions for notes, warnings and examples instead of writing "Note that ..." in the prose.
7. Do not add a FAQ. Answers belong in the page that covers the topic.

Component pages under `docs/packages/` all share one fixed shape, which is documented at the end of `docs/packages/index.md`.
Follow it when adding a component, and add the new page to the `nav` tree in `mkdocs.yml`.

## Checking your work

```bash title="Build the site the way CI does"
./serve build --strict
```

```bash title="Preview locally on http://127.0.0.1:8000"
./serve
```

`./serve` runs mkdocs through `uv tool run`, so [uv](https://docs.astral.sh/uv/getting-started/installation/) has to be installed, but no virtual environment is needed.
A `--strict` build has to pass before a documentation change is finished.

`--strict` does not catch a reference that is defined but misspelled at the point of use, so check that new references resolve in the generated HTML under `site/`, or by following the link in the local preview.

## The tools in `bin/`

The tools inspect a live Alps node or a mounted uenv, so their output cannot be reproduced on a development machine.
Do not invent, extrapolate or update the example output in the documentation.
If a table of versions needs to change, ask for output captured on the target system.

Three modules in `bin/` are imported by the tools rather than run.

| Module | What it holds | Imported by |
|---|---|---|
| `netstack.py` | The component record that both stack tools emit, the table renderer and `--format` flag every tool shares, and the helper that runs an external probe. | `system-stack`, `user-stack`, `spack-db` |
| `spackdb.py` | A read-only reader for a Spack database. | `user-stack`, `spack-db` |
| `rpmdb.py` | Read-only queries against the RPM database, by package name and by path. Both directions answer in one `rpm` call. | `system-stack`, `user-stack` |

A change to any of them affects every tool that imports it, and a change to the shape of a component record affects both stack tools and the documentation that shows their tables.

A tool declares *what* it collects and *which* columns it can fill, and never how a table is drawn: pretty, markdown and JSON are rendered from one column spec, so a column cannot appear in one format and be missing from another.
Check a change to any of them against a real node, and diff all three formats before and after.
