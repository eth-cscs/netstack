[](){#ref-pkg-aws-ofi-nccl}
# aws-ofi-nccl

aws-ofi-nccl is the plugin that lets [NCCL][ref-pkg-nccl] use [libfabric][ref-pkg-libfabric] as its network transport.
It is the bridge from GPU collectives onto the Slingshot fabric.

| Property | Value |
|---|---|
| Spack package | `aws-ofi-nccl` |
| Layer | GPU collectives (transport) |
| Provided by | User. |
| User-buildable | Yes. |
| Slingshot component | Yes, through the [libfabric][ref-pkg-libfabric] CXI provider. |
| Upstream | <https://github.com/aws/aws-ofi-nccl> |

## What it is

aws-ofi-nccl is a NCCL network plugin. It implements the NCCL net API on top of [libfabric][ref-pkg-libfabric].
The build produces `libnccl-net-ofi.so`, and NCCL sees it as `libnccl-net.so`.
It routes inter-node NCCL traffic through the `cxi` provider, [libcxi][ref-pkg-libcxi] and the Slingshot NIC. This is the same path that MPI takes.
When it is active, NCCL reports `NCCL_NET = AWS Libfabric`.

Its dependency tree links [libfabric][ref-pkg-libfabric], [libcxi][ref-pkg-libcxi] and the [CUDA runtime][ref-pkg-cuda] directly.

## System or user

aws-ofi-nccl is always a user component. The uenv ships it alongside [NCCL][ref-pkg-nccl].
Like NCCL, it depends on libfabric and CXI. The host or the uenv can provide these, so check each environment.

## Identifying it

[`user-stack`][ref-tools-user-stack] finds `libnccl-net-ofi.so` on the view path and reports its version from the Spack store directory.

| Environment | Version |
|---|---|
| `prgenv-gnu/25.11:v1` | 1.16.3 |
| `prgenv-gnu/25.6:v2` | 1.16.0 |
| `prgenv-gnu/24.7:v3` | master, from a git build |

The first check is whether `libnccl-net-ofi.so`, or `libnccl-net.so`, is present in the view.
Set `NCCL_DEBUG=INFO`. When the plugin loads, NCCL prints `Using network AWS Libfabric`. This confirms that the plugin is in use.

## Environment variables

You tune aws-ofi-nccl through the `OFI_NCCL_*` family, and you select it through NCCL's `NCCL_NET_PLUGIN`.
[Environment variables][ref-envvars-aws-ofi-nccl] lists both.

## Related

* [nccl][ref-pkg-nccl] is the library that this plugin plugs into.
* [libfabric][ref-pkg-libfabric] is the fabric abstraction it targets.
* [libcxi][ref-pkg-libcxi] is the Slingshot library underneath.
