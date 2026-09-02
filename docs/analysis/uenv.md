[](){#ref-analysis-uenv}
# Analysing a uenv

This page describes how the netstack of a uenv is extracted.
It is specific to uenv because, while the runtime-resolution method is general, the package-metadata half relies on the Spack database in the uenv.

A uenv is a SquashFS image that contains a Spack installation whose root is the mount point, `/user-environment` by default.
That gives two independent sources of truth, which the tools combine.

[](){#ref-analysis-uenv-discovery}
## Mount and view discovery

A loaded uenv describes itself through the environment.

| Variable | What it gives |
|---|---|
| `UENV_VIEW`, as `<mount>:<name>:<view>` | The mount point, the uenv name, and the active view. |
| `UENV_MOUNT_LIST`, as `<sqfs>:<mount>,…` | The mounted images and their mount points. |
| `UENV_TELEMETRY` | JSON holding the label, name, mount, views and image digest. |

The active view lives at `<mount>/env/<view>/{bin,lib,lib64}`, and it is what rewrites `PATH` and `LD_LIBRARY_PATH`.
It is therefore the starting point for finding the libraries that are "loaded and available".

[](){#ref-analysis-uenv-runtime}
## Runtime resolution

Starting from the anchor libraries on the view path, which are the MPI library, `libnccl` and the aws-ofi-nccl plugin, the full dependency tree is resolved with [libtree](https://github.com/haampie/libtree).

```bash title="Resolving the dependency tree of the MPI library"
libtree -p /user-environment/env/default/lib/libmpi_gnu_123.so.12
```

`libtree -p` is preferred over `ldd` for two reasons.
It resolves ELF dependencies statically, without executing the object, and it annotates how each library was found, as `[rpath]`, `[runpath]`, `[LD_LIBRARY_PATH]`, `[default path]` or `[ld.so.conf]`.

!!! example
    In `prgenv-gnu/25.6`, Cray MPICH is rpath-pinned to `/opt/cray/libfabric/1.22.0`, which is not the system default libfabric, and only the resolved path together with its search mechanism reveals that.
    `user-stack` displays it in the Found via column, and falls back to `ldd` if `libtree` is not installed, losing the annotation but keeping the resolved paths.

[](){#ref-analysis-uenv-provenance}
### Provenance by path

Provenance is never inferred from a library's name.
For each resolved dependency, its real path is tested against the uenv mount point:

1. a path under `<mount>` means the library is provided by the uenv, and
2. a path anywhere else, such as `/usr/lib64`, `/opt/cray/...` or `/opt/xpmem`, means it is provided by the host.

!!! example
    [libfabric][ref-pkg-libfabric] and [libcxi][ref-pkg-libcxi] are provided by the uenv in `prgenv-gnu/25.11`, and by the host in `25.6` and `24.7`.

[](){#ref-analysis-uenv-spack-db}
## The Spack database

Runtime resolution finds paths, and the Spack database says what those paths are.
Every installed package is recorded in `<mount>/.spack-db/index.json`, with its name, version, install prefix, dag-hash, and its dependency edges tagged as `build`, `link` or `run`.

The database is the source of truth for dependencies, and it exposes two things that runtime resolution cannot.

1. **Authoritative identity**: A resolved store path such as `…/libfabric-2.3.1-ekke44pq…/` maps through its trailing hash to the exact package record. `user-stack` attaches that hash to every uenv component it reports.
2. **Build-only dependencies**: Packages that produce no runtime object never appear in `ldd`, but do appear in the graph. The most important of these are the Slingshot [cassini-headers][ref-pkg-cassini-headers] and the [cxi-driver][ref-pkg-cxi-driver] headers.

!!! warning "The database does not always reflect the runtime environment"
    The database describes what the uenv was built against.
    For external packages it can diverge from what actually loads.

    Trust the database for the identity of in-uenv packages and for build dependencies, and trust runtime resolution for which host libraries load.

    !!! example
        On Alps the Spack `xpmem` external is recorded as version `2.9.6` under `/usr`, while the library that actually loads is the host copy in `/opt/xpmem`, which the RPM database calls `1.0.1`.
        `user-stack` reports `1.0.1` for that xpmem, because it asks the RPM database about the file that actually loaded rather than the Spack record of an external.


[](){#ref-analysis-uenv-build-provenance}
### Build provenance

Combining the two sources answers a question that matters for diagnosis: which NIC ABI was the fabric stack built against?

When [libfabric][ref-pkg-libfabric] and [libcxi][ref-pkg-libcxi] are uenv-provided, `user-stack` lists the [cassini-headers][ref-pkg-cassini-headers] and [cxi-driver][ref-pkg-cxi-driver] they were built against as components in their own right, with the version and dag-hash taken from the database and the fabric libraries they were compiled into named in the **Found via** column.
Those can then be compared against the host kernel [cxi-driver][ref-pkg-cxi-driver], which [`system-stack`][ref-tools-system-stack] reports.

The version those packages carry in the database is a Spack git version, which is a commit or a tag rather than a version of the package, so it is reported as an [SHS release][ref-shs-versions-uenv] in the `shs` field and the header rows carry no version of their own.

!!! example "A pairing that a compatibility check has to reason about"
    In `prgenv-gnu/25.11` the fabric libraries are built against Cassini headers from git `main`, while the host driver is version `1.0.0` from `SHS13.1.0`.
    Because that commit carries no release tag, `user-stack` reports the header version as unknown: the uenv cannot be placed on the [SHS][ref-shs] timeline at all.

[](){#ref-analysis-uenv-version-namespaces}
## Version namespaces

Different sources report different numbering schemes for one library.
A mismatch between them is expected, and is not a bug.

| Source         | Example for libcxi               | What the number is |
|---|---|---|
| RPM            | `1.0.2` in `SHS13.1.0`           | The host package version. |
| soname         | `1.5.0`, from `libcxi.so.1.5.0`  | The shared-object ABI version. |
| Spack database | `git.release/shs-13.0.0=13.0.0`  | The [SHS release][ref-shs] the uenv built, from a release tag. |
| Spack database | `git.be1f7149…=main`             | An untagged commit, which names no release. |

All of them are correct.
Compare like with like, by path, by hash, or by SHS release, and never across schemes.

The [component record][ref-tools-components] keeps them apart rather than choosing between them.
`version` is the number the component's own provider gives it, and `version_source` says which of the rows above it was read from: `rpm` for a host file the RPM database owns, `soname` or `store` for one resolved from a path.
A version read from an RPM is the plain release, with any vendor build stamp fused to its tail left in the origin rather than in the version column.
`shs` is reported separately, because the release is the only one of these numbers that means the same thing on both sides of the split.

[](){#ref-analysis-uenv-querying}
## Querying the database directly

Ad-hoc queries against the database of a mounted uenv are made with `spack-db`, which is documented in [Tools][ref-tools-spack-db].
