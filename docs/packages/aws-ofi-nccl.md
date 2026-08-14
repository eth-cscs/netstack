# aws-ofi-nccl

> The plugin that lets [NCCL][nccl] use [libfabric][libfabric] as its network
> transport — the bridge from GPU collectives onto the Slingshot fabric.

|  |  |
|---|---|
| Spack package | `aws-ofi-nccl` |
| Layer | GPU collectives (transport) |
| Provided by | **user** |
| User-buildable | yes |
| Slingshot component | ● (via the [libfabric][libfabric] CXI provider) |
| Upstream | <https://github.com/aws/aws-ofi-nccl> |

## What it is

aws-ofi-nccl is a NCCL **network plugin** (`libnccl-net-ofi.so`, exposed to NCCL
as `libnccl-net.so`) that implements NCCL's net API on top of
[libfabric][libfabric]. It is what routes inter-node NCCL traffic through the
`cxi` provider, [libcxi][libcxi] and the Slingshot NIC — the same path MPI takes.
When it is active, NCCL reports `NCCL_NET = AWS Libfabric`.

Its dependency tree links [libfabric][libfabric], [libcxi][libcxi] and the
[CUDA runtime][cuda] directly.

## System vs. user

Always a **user** component, shipped alongside [NCCL][nccl] in the uenv. Like
NCCL it depends on libfabric/CXI, whose provenance can be host or uenv — check
per environment.

## Identifying it

`bin/user-stack` finds `libnccl-net-ofi.so` on the view path and reports its
version from the Spack store directory:

| Environment | Version |
|---|---|
| `prgenv-gnu/25.11:v1` | 1.16.3 |
| `prgenv-gnu/25.6:v2`  | 1.16.0 |
| `prgenv-gnu/24.7:v3`  | master (git build) |

- Presence of `libnccl-net-ofi.so` (or `libnccl-net.so`) in the view.
- `NCCL_DEBUG=INFO` prints `Using network AWS Libfabric` when it loads.

## Environment variables

Tuned through the `OFI_NCCL_*` family and selected via NCCL's `NCCL_NET_PLUGIN`
— see [Environment variables][envvars].

## Related

- [nccl][nccl] — the library this plugs into.
- [libfabric][libfabric] — the fabric abstraction it targets.
- [libcxi][libcxi] — the Slingshot library underneath.

[nccl]: nccl.md
[libfabric]: libfabric.md
[libcxi]: libcxi.md
[cuda]: cuda.md
[envvars]: ../envvars.md
