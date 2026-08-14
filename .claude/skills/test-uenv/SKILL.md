---
name: test-uenv
description: >-
  Run a command inside a uenv (a SquashFS software-stack image with a "view")
  on Alps HPC systems, without dropping into an interactive sub-shell. Use when
  you need to inspect or test what is inside a uenv — e.g. run the netstack
  tools (bin/user-stack), check library versions, resolve dependency trees, or
  execute any command against the environment a uenv provides. Triggers:
  "test a uenv", "run inside a uenv", "what's in prgenv-gnu", "inspect a view".
---

# Testing a uenv non-interactively

A **uenv** is a SquashFS image mounted (by default) at `/user-environment`. A
**view** rewrites `PATH`, `LD_LIBRARY_PATH`, `CC`/`CXX`/`FC`, `MPICC`, etc. to
point into the image so the software inside it becomes the active toolchain.

The key command is `uenv run`, which mounts an image, activates a view, runs a
single command, and returns — **no interactive shell, no manual unload**. This
is exactly what you want when driving a uenv from a script or an agent:

```bash
uenv run --view=<view> <image> -- <CMD> [args...]
```

- `<image>` is `name/version:tag` (e.g. `prgenv-gnu/25.11:v1`) or an image id.
- `<view>` is a view name; `default` is the usual choice. `uenv run` also
  accepts `--view=<uenv>:<view>` when several images are stacked.
- Everything after `--` runs *inside* the activated environment and its stdout
  comes straight back to you.

## Recipes

Run this project's netstack reporter inside a uenv:

```bash
uenv run --view=default prgenv-gnu/25.11:v1 -- ./bin/user-stack
uenv run --view=default prgenv-gnu/25.11:v1 -- ./bin/user-stack --format json
```

Ad-hoc inspection (each `uenv run` is independent — chain with a sub-shell):

```bash
uenv run --view=default prgenv-gnu/25.11:v1 -- bash -c '
  mpichversion | head -1
  fi_info -l                 # libfabric providers actually available
  libtree -p $(which mpicc)  # dependency tree + how each lib was resolved
  env | grep -E "^(MPICH|FI_|NCCL)_"
'
```

## Discovering, checking, and fetching images

```bash
uenv image ls                       # images available locally
uenv image ls prgenv-gnu/25.11:v1   # filter to one image
uenv image inspect <image>          # show the views an image provides
```

Images in the repo index are **not** necessarily downloaded. If `uenv run`
reports `no uenv matches '<image>@<system>'` even though `uenv image ls` lists
it, the SquashFS blob is missing — pull it first:

```bash
uenv image pull <image>
```

## Gotchas

- **`no uenv matches` despite being listed** → the blob isn't downloaded; run
  `uenv image pull <image>` (see above). This is the most common failure.
- **Which view?** Run `uenv image inspect <image>` to list views. `prgenv-gnu`
  exposes `default`, `spack`, and `modules`; use `default` for the toolchain.
- **Provenance matters.** A library on `LD_LIBRARY_PATH` may still resolve to a
  *host* copy via rpath/default search. Use `libtree -p <lib>` (preferred) or
  `ldd <lib>` and check whether the resolved path is under `/user-environment`.
  `libtree -p` also annotates *how* each library was found (rpath, runpath,
  `LD_LIBRARY_PATH`, default path) — the signal `bin/user-stack` reports in its
  "Found via" column.
- **One command per `uenv run`.** State does not persist between invocations;
  wrap multiple steps in a single `bash -c '...'`.
