# libfabric

> The Open Fabrics Interfaces (OFI) — the fabric abstraction layer that MPI and
> NCCL talk to, and the home of the Slingshot **CXI** provider.

|  |  |
|---|---|
| Spack package | `libfabric` |
| Layer | fabric abstraction (OFI) |
| Provided by | **user *or* system** |
| User-buildable | yes |
| Slingshot component | ● (via the `cxi` provider) |
| Upstream | <https://libfabric.org/> |

## What it is

libfabric exports a single API (`libfabric.so.1`) over many transports, chosen
at runtime by **provider**. On Alps the provider that matters is **`cxi`** — the
HPE Slingshot-11 back-end that drives the NIC through [libcxi][libcxi] and the
[CXI driver][cxi-driver]. Everything above the fabric ([Cray MPICH][cray-mpich],
[NCCL][nccl] via [aws-ofi-nccl][aws-ofi-nccl]) reaches the network through
libfabric.

List the providers actually compiled in with `fi_info -l`, and the CXI domains
present on the node with `fi_info -p cxi`. On a Grace-Hopper node the providers
are `cxi`, `ofi_rxm`, `udp`, `tcp`, `sockets`, plus the `ofi_hook_*` hooks.

!!! warning "`strings libfabric.so` is not authoritative"
    A naive grep for provider names can miss `cxi`, which is compiled in but
    only confirmed by running `fi_info`. Always ask the library, don't guess.

## System vs. user

This is the clearest example of a component that lands on **either** side:

- **System.** The base image ships several copies under
  `/opt/cray/libfabric/<version>/` (e.g. `1.15.2.0`, `1.22.0`, `2.3.1`) plus a
  default `/usr/lib64/libfabric.so.1`. RPM: `libfabric` (`2.3.1`, `SHS13.1.0`).
- **User.** A uenv can ship its own libfabric and put it on the view path,
  replacing the system copy.

Which one loads is decided by the loader, not by the name — see below.

## Identifying it

`bin/user-stack` resolves the libfabric that the MPI library actually links, and
reports its origin and how it was found. Across the reference uenvs:

| Environment | Version | Origin | Found via |
|---|---|---|---|
| `prgenv-gnu/25.11:v1` | 2.3.1    | **uenv** | rpath |
| `prgenv-gnu/25.6:v2`  | 1.22.0   | host     | rpath |
| `prgenv-gnu/24.7:v3`  | 1.15.2.0 | host     | rpath |

Note that in `25.6` and `24.7` libfabric is **rpath-pinned by Cray MPICH** to a
specific `/opt/cray/libfabric/<ver>` — *not* the system default `2.3.1`. Only
the resolved path tells you the truth.

The store/path version (e.g. `2.3.1`) is the **release**; the soname
(`libfabric.so.1.29.1`) is the ABI version — different numbers for the same
library.

## Environment variables

The `FI_*` family, including the CXI-specific `FI_CXI_*` — see
[Environment variables][envvars]. `FI_MR_CACHE_MONITOR` and
`FI_CXI_RX_MATCH_MODE` are frequent diagnostic targets.

## Related

- [libcxi][libcxi] — the user-space library the CXI provider calls.
- [cxi-driver][cxi-driver] — the kernel driver underneath.
- [cassini-headers][cassini-headers] — build-time headers for the CXI provider.
- [aws-ofi-nccl][aws-ofi-nccl] — routes NCCL over this library.

[libcxi]: libcxi.md
[cxi-driver]: cxi-driver.md
[cassini-headers]: cassini-headers.md
[cray-mpich]: cray-mpich.md
[nccl]: nccl.md
[aws-ofi-nccl]: aws-ofi-nccl.md
[envvars]: ../envvars.md
