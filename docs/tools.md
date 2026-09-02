[](){#ref-tools}
# Tools

Three tools live in `bin/`.

| Tool | Reports | Where to run it |
|---|---|---|
| [`system-stack`][ref-tools-system-stack] | The system half of the stack, from the RPM database. | On a login or compute node. |
| [`user-stack`][ref-tools-user-stack] | The user half of a loaded uenv. | Inside `uenv run`. |
| [`spack-db`][ref-tools-spack-db] | The Spack package database of a uenv. | Inside `uenv run`, or anywhere with `--mount`. |

The tools share three small importable modules. `bin/netstack.py` defines the [component record][ref-tools-components] and renders it. `bin/spackdb.py` reads a Spack database. `bin/rpmdb.py` reads the RPM database.

All three tools take a `--format` option:

1. `pretty`, the default, prints a coloured table for the terminal.
2. `markdown` prints GitHub-flavoured tables. This page's tables were generated with it.
3. `json` prints machine-readable output for other tools to read.

!!! note
    Only `system-stack` and `user-stack` support `--format markdown`.

[Analysing an environment][ref-analysis] describes the method these tools implement, rather than their command line.

[](){#ref-tools-requirements}
## tool runtime requirements

The only runtime requirement to run the tools is [`uv`](https://docs.astral.sh/uv).

Each tool is a self-contained [uv](https://docs.astral.sh/uv/) script. It has a `#!/usr/bin/env -S uv run` shebang and an inline dependency block. You can run it directly, without first creating a virtual environment.

[](){#ref-tools-components}
## The component record

`system-stack` and `user-stack` report the two halves of one stack. They describe a component the same way.
Both print a `components` list. Every entry carries the same fields.

| Field | What it holds |
|---|---|
| `name` | The component name, from the same vocabulary on both sides: the [package pages][ref-pkg]. |
| `version` | The component's own version, in whatever scheme its provider names it. |
| `version_source` | Where that number was read: `rpm`, `store`, `path`, `soname`, `spack` or `runtime`. |
| `shs` | The [SHS release][ref-shs] the component belongs to. |
| `origin` | What supplied the component, or nothing at all when it is not present. |
| `prefix` | The install prefix. |
| `path` | The file that was resolved, for a component found by runtime resolution. |
| `via` | How the dynamic loader found it. |

`version` and `shs` answer different questions. A component can carry both.
The version is whatever its provider calls it, and the providers disagree: the same [libcxi][ref-pkg-libcxi] is `1.0.2` to RPM and `1.5.0` to its soname.
The SHS release is the one number both halves of a stack have in common. That is why it is a field of its own, not a version in disguise.
[How to detect the SHS version][ref-shs-versions] describes how each side gets it.

`origin` takes one of four forms. It holds the evidence specific to what supplied the component, not anything already reported at the top level.

| `origin.type` | The component came from | It also carries |
|---|---|---|
| `uenv` | A package the uenv built. | The mount point, the Spack dag-hash, and the version string as the database records it. |
| `rpm` | A package in the host image. | The full package name, and the version and release strings separately. |
| `host` | A file on the host that no RPM owns, such as `/opt/cray/libfabric/1.22.0`. | Nothing further. |
| nothing | The component was looked for and not found. | |

See [JSON output][ref-json-output] for the full record, including every `origin` variant.

A component that both tools see is the same component in both reports.
`user-stack` reads a host library from the same RPM database that `system-stack` queries. So the two agree on its version, its SHS release, and its origin. You can compare the halves field by field.

[](){#ref-tools-system-stack}
## system-stack

`system-stack` reports the [system components][ref-index-system]: the drivers and base-image libraries. It queries these from the RPM database.
It also reports a few system properties: the OS, the cluster, the NVIDIA driver and CUDA versions, and the installed GCC toolchains.

```bash title="Reporting the system half of the stack"
./bin/system-stack
```

Run it on a login or compute node, and not inside a uenv, because it reports the base system rather than user land.

It maps each logical component to one or more RPM names. For example, it maps `libfabric` to `libfabric`, and `libcxi` to `cray-libcxi`. It queries `rpm -q --queryformat`. It infers the install prefix from the package file list.
The `shs` field is the [HPE Slingshot Host Software][ref-shs] release that the package belongs to. `system-stack` parses it from the RPM release string, for example `SHS13.1.0`.
[How to detect the SHS version][ref-shs-versions] describes how each side recovers that release.

| Component       | Version   | SHS    | Origin   | Prefix                    |
|-----------------|-----------|--------|----------|---------------------------|
| cassini-headers | 1.1.2     | 13.1.0 | rpm      | /usr                      |
| libcxi          | 1.0.2     | 13.1.0 | rpm      | /usr                      |
| cxi-driver      | 1.0.0     | 13.1.0 | rpm      | /usr                      |
| libfabric       | 2.3.1     | 13.1.0 | rpm      | /opt/cray/libfabric/2.3.1 |
| slurm           | 25.05.8   | -      | rpm      | /usr                      |
| vast            | 4.5.8     | -      | rpm      | /                         |
| lustre          | 2.15.7    | -      | rpm      | /usr                      |
| xpmem           | 1.0.1     | -      | rpm      | /opt/xpmem                |

The version is the plain release. This is not always the whole of what the RPM declares.
A vendor build can fuse its own stamp onto the tail of the version. For example, the Lustre client is `2.15.7.2_cray_39_g654b360`. `system-stack` reports only the leading run of numeric components, and leaves the rest in the origin, where the `package` field names the exact build.
A component that is not installed keeps its row, with `not installed` in place of an origin. If an expected package is missing, that itself is a diagnosis.

[](){#ref-tools-user-stack}
## user-stack

`user-stack` reports the [user components][ref-index-user] of a loaded uenv view: MPI, GTL, libfabric and its providers, libcxi, the Slingshot headers the fabric libraries were built against, NCCL, aws-ofi-nccl, the CUDA runtime, XPMEM, and the launch stack of PMI, PMIx and PALS.
For each component it gives the [record][ref-tools-components] described above: the version, the SHS release where there is one, what supplied it, and how the dynamic loader found it.

Run it inside a uenv:

```bash title="Reporting the user half of a uenv"
uenv run --view=default prgenv-gnu/25.11:v1 -- ./bin/user-stack
```

MPI detection is flavour-aware.
`user-stack` recognises Cray MPICH, Open MPI, and upstream MPICH from the resolved Spack store directory. It reports the launch and GPU components that match that flavour: [cray-gtl][ref-pkg-cray-gtl], [cray-pmi][ref-pkg-cray-pmi], and [cray-pals][ref-pkg-cray-pals] for Cray MPICH, or [pmix][ref-pkg-pmix] for Open MPI.

| Component       | Version   | SHS   | Origin   | Found via                    | Hash    |
|-----------------|-----------|-------|----------|------------------------------|---------|
| cray-mpich      | 8.1.32    | -     | uenv     | view                         | j4gnffa |
| cray-gtl        | 8.1.32    | -     | uenv     | rpath                        | 3ixenfp |
| libfabric       | 2.3.1     | -     | uenv     | rpath                        | ekke44p |
| libcxi          | 1.5.0     | -     | uenv     | rpath                        | o5yivpa |
| cassini-headers | -         | -     | uenv     | built into libcxi, libfabric | b2rr3tx |
| cxi-driver      | -         | -     | uenv     | built into libcxi, libfabric | dqc4kbf |
| nccl            | 2.28.3    | -     | uenv     | view                         | 2s7ijuj |
| aws-ofi-nccl    | 1.16.3    | -     | uenv     | view                         | lkkfflf |
| cuda            | 12.9.0    | -     | uenv     | rpath                        | amizf2z |
| cuda-driver     | 590.48.01 | -     | rpm      | default path                 | -       |
| xpmem           | 1.0.1     | -     | rpm      | ld.so.conf                   | -       |
| cray-pmi        | 6.1.15    | -     | uenv     | rpath                        | r3hwks4 |

`user-stack` lists only components that are **actually present** in the stack.
It does not emit placeholder rows for things that are absent. This uenv uses no [cray-pals][ref-pkg-cray-pals] launcher library, so no such row appears.
The `origin.hash` field is the Spack dag-hash of the package that owns an in-uenv library. It is empty for anything the host provides.

The `origin.type` field distinguishes the three ways a component can reach the stack.
A `uenv` component is one the uenv built. `user-stack` identifies it through its Spack database.
An `rpm` component is a host file that `user-stack` looked up in the RPM database. That is why `cuda-driver` and `xpmem` above report a version and an origin at all.
A `host` component is a host file that no RPM owns, such as the Cray libfabric under `/opt/cray/libfabric/1.22.0` that older uenvs load. `user-stack` versions it from its path.

Two of the rows are not runtime libraries at all.
[cassini-headers][ref-pkg-cassini-headers] and [cxi-driver][ref-pkg-cxi-driver] are header-only packages compiled *into* the fabric libraries. They load nothing, so `ldd` cannot see them. `user-stack` recovers them from the build and link edges recorded in the Spack database. Their `via` field reads `built into <library>` instead of a loader search mechanism.
They pin the NIC and kernel-driver ABI that [libfabric][ref-pkg-libfabric] and [libcxi][ref-pkg-libcxi] were built against. This governs compatibility with the CXI driver that runs on the host.
Their `shs` field is the [release the uenv built them from][ref-shs-versions-uenv]. It is empty above because `prgenv-gnu/25.11` pinned an untagged commit instead of a release tag.
They only appear when the fabric libraries come from the uenv. If libfabric and libcxi are host-provided, there is no Spack package to read the edges from.
If two rows carry the same component name, that means libfabric and libcxi disagree on that ABI.

The same command, run against `prgenv-gnu/25.6:v2`, reports libfabric `1.22.0` from the host. It reports libcxi as `1.0.2` from the RPM `cray-libcxi`, in SHS `13.1.0`. These are the same numbers [`system-stack`][ref-tools-system-stack] reports for the host, because it is the same file.
The view has the same name in both uenvs. But the stack behind it differs.

[](){#ref-tools-spack-db}
## spack-db

A uenv is a Spack installation whose root is its mount point. `spack-db` answers questions against the database at `<mount>/.spack-db/index.json`.
That database is the source of truth for versions and dependencies. `user-stack` uses it to enrich its report.

```bash title="Querying the Spack database of a mounted uenv"
spack-db --mount /user-environment list                            # everything installed
spack-db --mount /user-environment list --name libfabric           # one package by name
spack-db --mount /user-environment show libfabric                  # package and direct deps
spack-db --mount /user-environment deps libfabric -t --type link   # transitive link deps
spack-db --mount /user-environment dependents libcxi               # what needs libcxi
spack-db --mount /user-environment owner <path-to-a-.so>           # which package owns a path
```

You can name a package by full hash, by a unique hash prefix, or by name.

!!! note "`--mount` is required"
    `--mount` names the Spack install root. For a uenv, this is its mount point, available as `$UENV_MOUNT` inside `uenv run`.
    You can give it before or after the subcommand.
