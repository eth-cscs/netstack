# Tools

Two reporters live in `bin/`. Both are self-contained
[`uv`](https://docs.astral.sh/uv/) scripts (a `#!/usr/bin/env -S uv run` shebang
with an inline dependency block) — run them directly, no virtualenv needed.

Each supports three output formats:

- `--format pretty` (default) — a coloured table for the terminal;
- `--format markdown` — GitHub-flavoured tables (used to generate these docs);
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
its providers, libcxi, NCCL, aws-ofi-nccl, the CUDA runtime, XPMEM, PMI and
PALS — with the version of each, whether it is uenv- or host-provided, and how
the loader found it.

Run it **inside** a uenv (see the [test-uenv](#) skill):

```console
$ uenv run --view=default prgenv-gnu/25.11:v1 -- ./bin/user-stack
```

Example (`prgenv-gnu/25.11:v1`):

| Component    | Version   | Origin | Found via    | Role |
|--------------|-----------|--------|--------------|------|
| cray-mpich   | 8.1.32    | uenv   | view         | MPI (Cray MPICH, ABI-compatible MPICH 3.4a2) |
| cray-gtl     | 8.1.32    | uenv   | rpath        | GPU transport layer (GPU-aware MPI) |
| libfabric    | 2.3.1     | uenv   | rpath        | OFI fabric abstraction |
| libcxi       | 1.5.0     | uenv   | rpath        | Slingshot (CXI) user-space library |
| nccl         | 2.28.3    | uenv   | view         | GPU collectives |
| aws-ofi-nccl | 1.16.3    | uenv   | view         | NCCL ↔ libfabric transport plugin |
| cuda         | 12.9.0    | uenv   | rpath        | CUDA runtime (toolkit) |
| cuda-driver  | 590.48.01 | host   | default path | CUDA driver (userspace stub) |
| xpmem        | –         | host   | ld.so.conf   | intra-node shared memory |
| cray-pmi     | 6.1.15    | uenv   | rpath        | process management interface |
| cray-pals    | –         | absent | –            | application launch service |

The same command against `prgenv-gnu/25.6:v2` reports **libfabric 1.22.0
(host)** and **libcxi (host)** instead — the same view name, a different stack.
That contrast is the whole point of the tool.

## How provenance is determined

Provenance (`uenv` vs `host`) is **never** inferred from a library's name. For
each component `user-stack`:

1. picks an *anchor* library that is actually on the view path (the MPI library,
   `libnccl`, the aws-ofi-nccl plugin);
2. resolves its full dependency tree with
   [`libtree -p`](https://github.com/haampie/libtree) — which reads the ELF
   statically (no execution, unlike `ldd`) and annotates **how** each library
   was found: `rpath`, `runpath`, `LD_LIBRARY_PATH`, `default path`,
   `ld.so.conf`;
3. for each netstack library, resolves the real path and checks whether it lies
   under the uenv mount (`/user-environment`) → **uenv**, otherwise → **host**;
4. extracts a version from the Spack store directory name, a version path
   segment (e.g. `/opt/cray/libfabric/1.22.0/`), or the resolved soname.

If `libtree` is not on `PATH` the tool falls back to `ldd`, losing only the
"Found via" annotation.

!!! note "Why *Found via* matters"
    A library on `LD_LIBRARY_PATH` is not necessarily the one that loads. In
    `prgenv-gnu/25.6`, Cray MPICH is **rpath-pinned** to
    `/opt/cray/libfabric/1.22.0`, even though the system default is a *different*
    libfabric (`2.3.1`). Only the resolved path and its search mechanism tell
    you what actually runs.

## Version namespaces — a caveat

The two tools can legitimately disagree on a version, because they report
different **numbering schemes**:

- `system-stack` reports the **RPM package version** (e.g.
  `cray-libcxi-1.0.2-SHS13.1.0`);
- `user-stack` reports the **shared-object (soname) version** it resolves (e.g.
  `libcxi.so.1.5.0`).

For [libcxi][libcxi] these are `1.0.2` and `1.5.0` respectively — both correct,
in different namespaces. When comparing across the two tools, compare like with
like (paths, or the SHS release).

[libcxi]: packages/libcxi.md
