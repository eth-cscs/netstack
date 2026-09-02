[](){#ref-analysis}
# Analysing an environment

To describe a netstack, you answer four questions for each component: What is it? What version is it? Does it come from the system or from the user? What does it depend on?
You need two kinds of evidence to answer these questions well.

Runtime resolution
:   This shows which shared objects a program actually loads.
    It also shows how the loader found each one: through an rpath, a runpath, `LD_LIBRARY_PATH`, `ld.so.conf`, or the default search path.
    This is the ground truth of what runs.
    You get it with `libtree` or `ldd`.

Package metadata
:   This is the identity and dependency graph of the installed software.
    It includes build-only dependencies that never appear at run time, such as the [Cassini headers][ref-pkg-cassini-headers] used to build a fabric library.
    Where this comes from depends on how the environment was built.

The two are complementary.
Runtime resolution shows what loads, and metadata shows what it is and what it was built from.
Neither is enough alone: a library on `LD_LIBRARY_PATH` can still resolve to a host copy through an rpath, and a build-time header mismatch stays invisible to `ldd`.

!!! note "Provenance is not decided by a library's name"
    The same library name can fall on either side of the split, depending on how the environment was built.
    `prgenv-gnu/25.11` ships its own libfabric and libcxi, while `prgenv-gnu/25.6` uses the host copies of both.
    You establish provenance by resolving the path that the dynamic loader actually uses, then cross-checking it against the Spack database of the uenv, as described in [Analysing a uenv][ref-analysis-uenv].


[](){#ref-analysis-environment-types}
## Environment types

The runtime-resolution half is the same for every kind of environment.
Only the metadata half changes, because how you get package metadata depends on how the environment was assembled.
Netstack adds one new environment type at a time.

| Environment | Metadata source | Status |
|---|---|---|
| [uenv][ref-analysis-uenv] | Spack database at `<mount>/.spack-db/index.json` | Supported |
| Container image | Image labels, or the package manager database inside the image | Planned |
| Python virtual environment | `pip` and `uv` metadata, `importlib.metadata` | Planned |

[Analysing a uenv][ref-analysis-uenv] documents the current implementation and its method.
It covers mount and view discovery, runtime resolution, the Spack database, provenance, build provenance, and version namespaces.
