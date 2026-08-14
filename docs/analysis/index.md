# Analysing an environment

Describing a netstack means answering, for every component: **what is it, what
version, where did it come from (system or user), and what does it depend on?**
Answering well needs *two* kinds of evidence:

1. **Runtime resolution** — which shared objects a program actually loads, and
   *how* the loader found each one (rpath, runpath, `LD_LIBRARY_PATH`, default
   search). This is the ground truth of what runs. Tools: `libtree`, `ldd`.
2. **Package metadata** — the identity and dependency graph of the installed
   software, including **build-only** dependencies that never appear at runtime
   (e.g. the [Cassini headers][cassini-headers] a fabric library was compiled
   against). The source depends on how the environment was built.

The two are complementary: runtime resolution says *what loads*, metadata says
*what it is and what it was built from*. Neither alone is enough — a library on
`LD_LIBRARY_PATH` may resolve to a host copy via rpath, and a build-time header
mismatch is invisible to `ldd`.

## Environment types

How the **package metadata** is obtained is specific to how the environment was
assembled. Support is being added one environment type at a time:

| Environment | Metadata source | Status |
|---|---|---|
| [**uenv**][uenv-analysis] | Spack database (`<mount>/.spack-db/index.json`) | supported |
| Container image | image labels / package manager db | planned |
| Python / venv | `pip`/`uv` metadata, `importlib.metadata` | planned |

The **runtime-resolution** half (`libtree`/`ldd` + provenance-by-path) is common
to all of them; only the metadata half changes. The current implementation and
methodology are documented for uenvs:

- [**Analysing a uenv**][uenv-analysis] — mount and view discovery, runtime
  resolution, the Spack database, provenance, build provenance, and version
  namespaces.

[uenv-analysis]: uenv.md
[cassini-headers]: ../packages/cassini-headers.md
