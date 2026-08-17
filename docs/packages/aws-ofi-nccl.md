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

aws-ofi-nccl is a NCCL network plugin, built as `libnccl-net-ofi.so` and exposed to NCCL as `libnccl-net.so`, that implements the NCCL net API on top of [libfabric][ref-pkg-libfabric].
It routes inter-node NCCL traffic through the `cxi` provider, [libcxi][ref-pkg-libcxi] and the Slingshot NIC, which is the same path that MPI takes.
When it is active, NCCL reports `NCCL_NET = AWS Libfabric`.

Its dependency tree links [libfabric][ref-pkg-libfabric], [libcxi][ref-pkg-libcxi] and the [CUDA runtime][ref-pkg-cuda] directly.

## System or user

aws-ofi-nccl is always a user component, shipped alongside [NCCL][ref-pkg-nccl] in the uenv.
Like NCCL it depends on libfabric and CXI, whose provenance can be either host or uenv, so check it per environment.

## Identifying it

[`user-stack`][ref-tools-user-stack] finds `libnccl-net-ofi.so` on the view path and reports its version from the Spack store directory.

| Environment | Version |
|---|---|
| `prgenv-gnu/25.11:v1` | 1.16.3 |
| `prgenv-gnu/25.6:v2` | 1.16.0 |
| `prgenv-gnu/24.7:v3` | master, from a git build |

The presence of `libnccl-net-ofi.so`, or of `libnccl-net.so`, in the view is the first check.
With `NCCL_DEBUG=INFO` set, NCCL prints `Using network AWS Libfabric` when the plugin loads, which confirms that it is actually in use.

## Environment variables

aws-ofi-nccl is tuned through the `OFI_NCCL_*` family, and it is selected through NCCL's `NCCL_NET_PLUGIN`.
Both are listed under [Environment variables][ref-envvars-aws-ofi-nccl].

## Related

* [nccl][ref-pkg-nccl] is the library that this plugin plugs into.
* [libfabric][ref-pkg-libfabric] is the fabric abstraction it targets.
* [libcxi][ref-pkg-libcxi] is the Slingshot library underneath.
