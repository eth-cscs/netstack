[](){#ref-analysis-uenv}
# Analysing a uenv

This page describes how to extract the netstack of a uenv.
It applies only to uenv. The runtime-resolution method is general, but the package-metadata half relies on the Spack database in the uenv.

A uenv is a SquashFS image. It contains a Spack installation whose root is the mount point, `/user-environment` by default.
This gives two independent sources of truth. The tools combine them.

[](){#ref-analysis-uenv-discovery}
## Mount and view discovery

A loaded uenv describes itself through the environment.

| Variable | What it gives |
|---|---|
| `UENV_VIEW`, as `<mount>:<name>:<view>` | The mount point, the uenv name, and the active view. |
| `UENV_MOUNT_LIST`, as `<sqfs>:<mount>,…` | The mounted images and their mount points. |
| `UENV_TELEMETRY` | JSON holding the label, name, mount, views and image digest. |

The active view lives at `<mount>/env/<view>/{bin,lib,lib64}`. It rewrites `PATH` and `LD_LIBRARY_PATH`.
It is therefore the starting point to find the libraries that are "loaded and available".

[](){#ref-analysis-uenv-runtime}
## Runtime resolution

The anchor libraries on the view path are the MPI library, `libnccl`, and the aws-ofi-nccl plugin. [libtree](https://github.com/haampie/libtree) resolves the full dependency tree, starting from these anchor libraries.

```bash title="Resolving the dependency tree of the MPI library"
libtree -p /user-environment/env/default/lib/libmpi_gnu_123.so.12
```

Two reasons make `libtree -p` better than `ldd`.
It resolves ELF dependencies statically. It does not run the object.
It also labels how the loader found each library: as `[rpath]`, `[runpath]`, `[LD_LIBRARY_PATH]`, `[default path]`, or `[ld.so.conf]`.

!!! example
    In `prgenv-gnu/25.6`, an rpath pins Cray MPICH to `/opt/cray/libfabric/1.22.0`. This is not the system default libfabric. Only the resolved path, together with its search mechanism, reveals that.
    `user-stack` reports it in the `via` field. If `libtree` is not installed, `user-stack` falls back to `ldd`. This loses the annotation but keeps the resolved paths.

[](){#ref-analysis-uenv-provenance}
### Provenance by path

You never infer provenance from a library's name.
For each resolved dependency, the tools test its real path against the uenv mount point:

1. A path under `<mount>` means the uenv provides the library.
2. A path anywhere else, such as `/usr/lib64`, `/opt/cray/...`, or `/opt/xpmem`, means the host provides it.

!!! example
    The uenv provides [libfabric][ref-pkg-libfabric] and [libcxi][ref-pkg-libcxi] in `prgenv-gnu/25.11`. The host provides them in `25.6` and `24.7`.

[](){#ref-analysis-uenv-spack-db}
## The Spack database

Runtime resolution finds paths, and the Spack database says what those paths are.
`<mount>/.spack-db/index.json` records every installed package, with its name, version, install prefix, dag-hash, and its dependency edges tagged as `build`, `link`, or `run`.

The database is the source of truth for dependencies. It exposes two things that runtime resolution cannot find.

1. **Authoritative identity**: A resolved store path such as `…/libfabric-2.3.1-ekke44pq…/` maps through its trailing hash to the exact package record. `user-stack` attaches that hash to every uenv component it reports.
2. **Build-only dependencies**: Packages that produce no runtime object never appear in `ldd`, but do appear in the graph. The most important of these are the Slingshot [cassini-headers][ref-pkg-cassini-headers] and the [cxi-driver][ref-pkg-cxi-driver] headers.

!!! warning "The database does not always reflect the runtime environment"
    The database describes what the uenv was built against.
    For external packages it can diverge from what actually loads.

    Trust the database for the identity of in-uenv packages and for build dependencies. Trust runtime resolution for which host libraries load.

    !!! example
        On Alps, the Spack database records the `xpmem` external as version `2.9.6` under `/usr`. But the library that actually loads is the host copy in `/opt/xpmem`. The RPM database calls that copy `1.0.1`.
        `user-stack` reports `1.0.1` for that xpmem. It asks the RPM database about the file that actually loaded, rather than the Spack record of an external.


[](){#ref-analysis-uenv-build-provenance}
### Build provenance

If you combine the two sources, you can answer a question that matters for diagnosis: which NIC ABI did the build target for the fabric stack?

When the uenv provides [libfabric][ref-pkg-libfabric] and [libcxi][ref-pkg-libcxi], `user-stack` lists the [cassini-headers][ref-pkg-cassini-headers] and [cxi-driver][ref-pkg-cxi-driver] they were built against as components in their own right. It takes their version and dag-hash from the database. The `via` field names the fabric libraries they were compiled into.
You can then compare those against the host kernel [cxi-driver][ref-pkg-cxi-driver]. [`system-stack`][ref-tools-system-stack] reports that driver.

The version those packages carry in the database is a Spack git version. This is a commit or a tag, not a package version. `user-stack` reports it as an [SHS release][ref-shs-versions-uenv] in the `shs` field instead. The header rows carry no version of their own.

!!! example "A pairing a compatibility check must reason about"
    In `prgenv-gnu/25.11`, the fabric libraries are built against Cassini headers from git `main`. The host driver is version `1.0.0` from `SHS13.1.0`.
    That commit carries no release tag. So `user-stack` reports the header version as unknown, and you cannot place the uenv on the [SHS][ref-shs] timeline at all.

[](){#ref-analysis-uenv-version-namespaces}
## Version namespaces

Different sources report different numbering schemes for one library.
A mismatch between them is normal. It is not a bug.

| Source         | Example for libcxi               | What the number is |
|---|---|---|
| RPM            | `1.0.2` in `SHS13.1.0`           | The host package version. |
| soname         | `1.5.0`, from `libcxi.so.1.5.0`  | The shared-object ABI version. |
| Spack database | `git.release/shs-13.0.0=13.0.0`  | The [SHS release][ref-shs] the uenv built, from a release tag. |
| Spack database | `git.be1f7149…=main`             | An untagged commit that names no release. |

All of them are correct.
Compare like with like: by path, by hash, or by SHS release. Never compare across schemes.

The [component record][ref-tools-components] keeps them apart. It does not choose between them.
`version` is the number the component's own provider gives it. `version_source` names the row above that the value came from: `rpm` for a host file the RPM database owns, `soname` or `store` for one resolved from a path.
A version read from an RPM is the plain release. Any vendor build stamp fused to its tail goes into `origin.version`, not into `version`.
The tools report `shs` separately, because the release is the only one of these numbers that means the same thing on both sides of the split.

[](){#ref-analysis-uenv-querying}
## Querying the database directly

Use `spack-db` to run ad-hoc queries against the database of a mounted uenv. [Tools][ref-tools-spack-db] documents it.
