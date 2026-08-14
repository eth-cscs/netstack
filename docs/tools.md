# Tools

Three tools live in `bin/`, all self-contained
[`uv`](https://docs.astral.sh/uv/) scripts (a `#!/usr/bin/env -S uv run` shebang
with an inline dependency block) — run them directly, no virtualenv needed:

| Tool | Reports | Run |
|---|---|---|
| `system-stack` | system half (RPM-based) | on a login / compute node |
| `user-stack`   | user half of a loaded uenv | inside `uenv run` |
| `spack-db`     | a uenv's Spack package database | inside `uenv run` (or `--mount`) |

`user-stack` and `spack-db` share a small importable module, `bin/spackdb.py`,
that reads the Spack database. Output formats:

- `--format pretty` (default) — a coloured table for the terminal;
- `--format markdown` — GitHub-flavoured tables (used to generate these docs;
  `system-stack` / `user-stack` only);
- `--format json` — machine-readable, for downstream tooling.

## `system-stack` — the system half

Reports the **system components**: drivers and base-image libraries, queried
from the RPM database, plus a few system properties (OS, cluster, NVIDIA driver
and CUDA version) and the installed GCC toolchains.

```console
$ ./bin/system-stack
```

It works by mapping each logical component to one or more RPM names
(`libfabric` → `libfabric`, `libcxi` → `cray-libcxi`, …), querying
`rpm -q --queryformat`, and inferring the install prefix from the package file
list. The **SHS** column is the HPE Slingshot Host Software release the package
belongs to, parsed from the RPM release string (e.g. `SHS13.1.0`).

Run it on a login or compute node — **not** inside a uenv, since it reports the
base system, not user-land.

## `user-stack` — the user half

Reports the **user components** of a *loaded uenv view*: MPI, GTL, libfabric and
its providers, libcxi, NCCL, aws-ofi-nccl, the CUDA runtime, XPMEM, and the
launch stack (PMI / PMIx / PALS) — with the version of each, whether it is uenv-
or host-provided, and how the loader found it.

MPI detection is **flavour-aware**: it recognises Cray MPICH, Open MPI, and
upstream MPICH from the resolved Spack store directory, and reports the
launch/GPU components that match — [cray-gtl][cray-gtl] + [cray-pmi][cray-pmi] +
[cray-pals][cray-pals] for Cray MPICH, or [pmix][pmix] for Open MPI.

Run it **inside** a uenv (see the [test-uenv](#) skill):

```console
$ uenv run --view=default prgenv-gnu/25.11:v1 -- ./bin/user-stack
```

Example (`prgenv-gnu/25.11:v1`):

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
| cray-pals    | –         | absent | –            | –       | application launch service |

The **Hash** column is the Spack dag-hash of the package that owns each in-uenv
library (blank for host / absent) — the authoritative identity, obtained from
the uenv's Spack database. Below the components, `user-stack` also prints a
**Slingshot build provenance** table: the [cassini-headers][cassini-headers] and
[cxi-driver][cxi-driver] each uenv-provided [libfabric][libfabric] / [libcxi][libcxi]
was *built against* — a build-time fact invisible to `ldd`.

The same command against `prgenv-gnu/25.6:v2` reports **libfabric 1.22.0
(host)** and **libcxi (host)** instead — the same view name, a different stack.
That contrast is the whole point of the tool.

## `spack-db` — querying the Spack database

A uenv is a Spack installation rooted at its mount point; `spack-db` answers
questions against its database (`<mount>/.spack-db/index.json`) — the source of
truth for versions and dependencies that `user-stack` uses to enrich its report.

```console
$ spack-db --mount /user-environment list                 # everything installed
$ spack-db --mount /user-environment show libfabric        # package + direct deps
$ spack-db --mount /user-environment deps libfabric -t --type link  # transitive link deps
$ spack-db --mount /user-environment dependents libcxi     # what needs libcxi
$ spack-db --mount /user-environment owner <path-to-a-.so> # which package owns a path
```

A package is named by full hash, unique hash prefix, or name. **`--mount` is
required** — it names the Spack install root (a uenv's mount point) and may be
given before or after the subcommand. `--format json` gives machine-readable
output.

## How environments are analysed

The methodology — mount/view discovery, runtime resolution with `libtree`,
provenance-by-path, the Spack database, build provenance, and the version-
namespace caveat — is documented under
[Analysing an environment › Analysing a uenv][uenv-analysis]. That section is
uenv-specific by design; container and Python-environment support will be added
alongside it.

[libfabric]: packages/libfabric.md
[libcxi]: packages/libcxi.md
[cassini-headers]: packages/cassini-headers.md
[cxi-driver]: packages/cxi-driver.md
[cray-gtl]: packages/cray-gtl.md
[cray-pmi]: packages/cray-pmi.md
[cray-pals]: packages/cray-pals.md
[pmix]: packages/pmix.md
[uenv-analysis]: analysis/uenv.md
