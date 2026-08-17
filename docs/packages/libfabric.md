[](){#ref-pkg-libfabric}
# libfabric

libfabric implements the Open Fabrics Interfaces, the fabric abstraction layer that MPI and NCCL talk to, and it is where the Slingshot CXI provider lives.

| Property | Value |
|---|---|
| Spack package | `libfabric` |
| Layer | Fabric abstraction (OFI) |
| Provided by | User or system. |
| User-buildable | Yes. |
| Slingshot component | Yes, through the `cxi` provider. |
| Upstream | <https://libfabric.org/> |

## What it is

libfabric exports a single API, `libfabric.so.1`, over many transports, and chooses between them at run time by selecting a provider.
On Alps the provider that matters is `cxi`, the HPE Slingshot 11 back end that drives the NIC through [libcxi][ref-pkg-libcxi] and the [CXI driver][ref-pkg-cxi-driver].
Everything above the fabric, meaning [Cray MPICH][ref-pkg-cray-mpich] and [NCCL][ref-pkg-nccl] through [aws-ofi-nccl][ref-pkg-aws-ofi-nccl], reaches the network through libfabric.

```console title="Listing the providers and the CXI domains on a node"
$ fi_info -l
$ fi_info -p cxi
```

On a Grace-Hopper node the compiled-in providers are `cxi`, `ofi_rxm`, `udp`, `tcp` and `sockets`, along with the `ofi_hook_*` hooks.

!!! warning "`strings libfabric.so` is not authoritative"
    Grepping the library for provider names can miss `cxi`, which is compiled in but only confirmed by running `fi_info`.
    Ask the library rather than guessing.

## System or user

libfabric is the clearest example of a component that lands on either side of the split.

System
:   The base image ships several copies under `/opt/cray/libfabric/<version>/`, for example `1.15.2.0`, `1.22.0` and `2.3.1`, plus a default `/usr/lib64/libfabric.so.1`.
    The RPM is `libfabric`, version `2.3.1` in `SHS13.1.0`.

User
:   A uenv can ship its own libfabric and put it on the view path, where it replaces the system copy.

Which one loads is decided by the loader, not by the name.

## Identifying it

[`user-stack`][ref-tools-user-stack] resolves the libfabric that the MPI library actually links, and reports its origin along with how the loader found it.

| Environment | Version | Origin | Found via |
|---|---|---|---|
| `prgenv-gnu/25.11:v1` | 2.3.1 | uenv | rpath |
| `prgenv-gnu/25.6:v2` | 1.22.0 | host | rpath |
| `prgenv-gnu/24.7:v3` | 1.15.2.0 | host | rpath |

In `25.6` and `24.7`, libfabric is rpath-pinned by Cray MPICH to a specific `/opt/cray/libfabric/<version>`, and not to the system default `2.3.1`.
Only the resolved path shows this.

!!! note "Release version and ABI version are different numbers"
    The store or path version, for example `2.3.1`, is the release.
    The soname, for example `libfabric.so.1.29.1`, is the ABI version.
    See [version namespaces][ref-analysis-uenv-version-namespaces].

## Environment variables

libfabric reads the `FI_*` family, including the CXI-specific `FI_CXI_*` variables, which are listed under [Environment variables][ref-envvars-libfabric].
`FI_MR_CACHE_MONITOR` and `FI_CXI_RX_MATCH_MODE` are frequent diagnostic targets.

## Related

* [libcxi][ref-pkg-libcxi] is the user-space library that the CXI provider calls.
* [cxi-driver][ref-pkg-cxi-driver] is the kernel driver underneath.
* [cassini-headers][ref-pkg-cassini-headers] provides the build-time headers for the CXI provider.
* [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] routes NCCL traffic over this library.
