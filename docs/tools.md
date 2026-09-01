[](){#ref-tools}
# Tools

Three tools live in `bin/`.
Each one is a self-contained [uv](https://docs.astral.sh/uv/) script, with a `#!/usr/bin/env -S uv run` shebang and an inline dependency block, so it can be run directly without creating a virtual environment first.

| Tool | Reports | Where to run it |
|---|---|---|
| [`system-stack`][ref-tools-system-stack] | The system half of the stack, from the RPM database. | On a login or compute node. |
| [`user-stack`][ref-tools-user-stack] | The user half of a loaded uenv. | Inside `uenv run`. |
| [`spack-db`][ref-tools-spack-db] | The Spack package database of a uenv. | Inside `uenv run`, or anywhere with `--mount`. |

`user-stack` and `spack-db` share a small importable module, `bin/spackdb.py`, which reads the Spack database.

All three tools take a `--format` option:

1. `pretty`, the default, prints a coloured table for the terminal,
2. `markdown` prints GitHub-flavoured tables, and is how the tables on these pages were generated, and
3. `json` prints machine-readable output for downstream tooling.

!!! note
    `--format markdown` is supported by `system-stack` and `user-stack` only.

The method that these tools implement, rather than their command line, is described in [Analysing an environment][ref-analysis].

[](){#ref-tools-system-stack}
## system-stack

`system-stack` reports the [system components][ref-index-system]: the drivers and base-image libraries, queried from the RPM database.
It also reports a few system properties, namely the OS, the cluster, the NVIDIA driver and CUDA versions, and the installed GCC toolchains.

```bash title="Reporting the system half of the stack"
./bin/system-stack
```

Run it on a login or compute node, and not inside a uenv, because it reports the base system rather than user land.

It works by mapping each logical component to one or more RPM names, for example `libfabric` to `libfabric` and `libcxi` to `cray-libcxi`, querying `rpm -q --queryformat`, and inferring the install prefix from the package file list.
The SHS column is the HPE Slingshot Host Software release that the package belongs to, parsed from the RPM release string, for example `SHS13.1.0`.

[](){#ref-tools-user-stack}
## user-stack

`user-stack` reports the [user components][ref-index-user] of a loaded uenv view: MPI, GTL, libfabric and its providers, libcxi, NCCL, aws-ofi-nccl, the CUDA runtime, XPMEM, and the launch stack of PMI, PMIx and PALS.
For each component it gives the version, whether the component is provided by the uenv or by the host, and how the dynamic loader found it.

Run it inside a uenv:

```bash title="Reporting the user half of a uenv"
uenv run --view=default prgenv-gnu/25.11:v1 -- ./bin/user-stack
```

MPI detection is flavour-aware.
`user-stack` recognises Cray MPICH, Open MPI and upstream MPICH from the resolved Spack store directory, and reports the launch and GPU components that match that flavour: [cray-gtl][ref-pkg-cray-gtl], [cray-pmi][ref-pkg-cray-pmi] and [cray-pals][ref-pkg-cray-pals] for Cray MPICH, or [pmix][ref-pkg-pmix] for Open MPI.

| Component    | Version   | Origin | Found via    | Hash    | Role |
|--------------|-----------|--------|--------------|---------|------|
| cray-mpich   | 8.1.32    | uenv   | view         | j4gnffa | MPI (Cray MPICH, ABI-compatible MPICH 3.4a2) |
| cray-gtl     | 8.1.32    | uenv   | rpath        | 3ixenfp | GPU transport layer (GPU-aware MPI) |
| libfabric    | 2.3.1     | uenv   | rpath        | ekke44p | OFI fabric abstraction |
| libcxi       | 1.5.0     | uenv   | rpath        | o5yivpa | Slingshot (CXI) user-space library |
| nccl         | 2.28.3    | uenv   | view         | 2s7ijuj | GPU collectives |
| aws-ofi-nccl | 1.16.3    | uenv   | view         | lkkfflf | NCCL ↔ libfabric transport plugin |
| cuda         | 12.9.0    | uenv   | rpath        | amizf2z | CUDA runtime (toolkit) |
| cuda-driver  | 590.48.01 | host   | default path | –       | CUDA driver (userspace stub) |
| xpmem        | –         | host   | ld.so.conf   | –       | intra-node shared memory |
| cray-pmi     | 6.1.15    | uenv   | rpath        | r3hwks4 | process management interface |

Only components that are **actually present** in the stack are listed —
`user-stack` does not emit placeholder rows for things that are absent (this
uenv, for example, uses no `cray-pals` launcher library, so it simply does not
appear). The **Hash** column is the Spack dag-hash of the package that owns each
in-uenv library (blank for host-provided libraries) — the authoritative
identity, obtained from the uenv's Spack database. Below the components,
`user-stack` also prints a
**Slingshot build provenance** table: the [cassini-headers][cassini-headers] and
[cxi-driver][cxi-driver] each uenv-provided [libfabric][libfabric] / [libcxi][libcxi]
was *built against* — a build-time fact invisible to `ldd`.

Below the component table, `user-stack` prints a Slingshot build provenance table.
For each uenv-provided [libfabric][ref-pkg-libfabric] and [libcxi][ref-pkg-libcxi] it gives the [cassini-headers][ref-pkg-cassini-headers] and [cxi-driver][ref-pkg-cxi-driver] that the library was built against, which is a build-time fact that `ldd` cannot show.

The same command run against `prgenv-gnu/25.6:v2` reports libfabric 1.22.0 and libcxi as host-provided instead.
The view has the same name in both uenvs, and the stack behind it is different.

[](){#ref-tools-spack-db}
## spack-db

A uenv is a Spack installation whose root is its mount point, and `spack-db` answers questions against the database at `<mount>/.spack-db/index.json`.
That database is the source of truth for versions and dependencies that `user-stack` uses to enrich its report.

```bash title="Querying the Spack database of a mounted uenv"
spack-db --mount /user-environment list                            # everything installed
spack-db --mount /user-environment list --name libfabric           # one package by name
spack-db --mount /user-environment show libfabric                  # package and direct deps
spack-db --mount /user-environment deps libfabric -t --type link   # transitive link deps
spack-db --mount /user-environment dependents libcxi               # what needs libcxi
spack-db --mount /user-environment owner <path-to-a-.so>           # which package owns a path
```

A package is named by full hash, by a unique hash prefix, or by name.

!!! note "`--mount` is required"
    `--mount` names the Spack install root, which for a uenv is its mount point, available as `$UENV_MOUNT` inside `uenv run`.
    It may be given before or after the subcommand.
