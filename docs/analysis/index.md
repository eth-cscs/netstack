[](){#ref-analysis}
# Analysing an environment

Describing a netstack means answering four questions for every component: what is it, which version is it, did it come from the system or from the user, and what does it depend on?
Answering them well needs two kinds of evidence.

Runtime resolution
:   Which shared objects a program actually loads, and how the loader found each one, whether through an rpath, a runpath, `LD_LIBRARY_PATH`, `ld.so.conf` or the default search path.
    This is the ground truth of what runs.
    It is obtained with `libtree` or `ldd`.

Package metadata
:   The identity and dependency graph of the installed software, including build-only dependencies that never appear at run time, such as the [Cassini headers][ref-pkg-cassini-headers] that a fabric library was compiled against.
    Where this comes from depends on how the environment was built.

The two are complementary.
Runtime resolution says what loads, and metadata says what it is and what it was built from.
Neither is sufficient alone: a library sitting on `LD_LIBRARY_PATH` may still resolve to a host copy through an rpath, and a build-time header mismatch is invisible to `ldd`.

!!! note "Provenance is not decided by a library's name"
    The same library name falls on either side of the split depending on how the environment was built.
    `prgenv-gnu/25.11` ships its own libfabric and libcxi, while `prgenv-gnu/25.6` uses the host copies of both.
    Provenance is established by resolving the path that the dynamic loader actually uses, then cross-checking it against the Spack database of the uenv, as described in [Analysing a uenv][ref-analysis-uenv].


[](){#ref-analysis-environment-types}
## Environment types

The runtime-resolution half is common to every kind of environment.
Only the metadata half changes, because how package metadata is obtained depends on how the environment was assembled.
Support is being added one environment type at a time.

| Environment | Metadata source | Status |
|---|---|---|
| [uenv][ref-analysis-uenv] | Spack database at `<mount>/.spack-db/index.json` | Supported |
| Container image | Image labels, or the package manager database inside the image | Planned |
| Python virtual environment | `pip` and `uv` metadata, `importlib.metadata` | Planned |

The current implementation and its methodology are documented in [Analysing a uenv][ref-analysis-uenv], which covers mount and view discovery, runtime resolution, the Spack database, provenance, build provenance, and version namespaces.
