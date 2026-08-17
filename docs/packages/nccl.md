[](){#ref-pkg-nccl}
# nccl

NCCL is NVIDIA's collective communication library, used for multi-GPU and multi-node reductions, broadcasts and all-gathers.

| Property | Value |
|---|---|
| Spack package | `nccl` |
| Layer | GPU collectives |
| Provided by | User. |
| User-buildable | Yes. |
| Slingshot component | Indirectly, through [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] and [libfabric][ref-pkg-libfabric]. |
| Upstream | <https://github.com/NVIDIA/nccl> |

## What it is

NCCL, as `libnccl.so.2`, implements optimized primitives for collective communication between GPUs.
Inside a node it uses NVLink and PCIe directly.
Across nodes it needs a network transport plugin, and on Alps that plugin is [aws-ofi-nccl][ref-pkg-aws-ofi-nccl], which carries NCCL traffic over [libfabric][ref-pkg-libfabric] and the CXI provider.
NCCL and MPI therefore share the same Slingshot fabric.

## System or user

NCCL is always a user component.
It ships in the uenv, or in a container or a `pip` wheel, and it sits on the view path.
It links the [CUDA runtime][ref-pkg-cuda].

## Identifying it

The soname carries the full release, so [`user-stack`][ref-tools-user-stack] reads the version from it directly.

| Environment | Version |
|---|---|
| `prgenv-gnu/25.11:v1` | 2.28.3 |
| `prgenv-gnu/25.6:v2` | 2.27.5 |
| `prgenv-gnu/24.7:v3` | 2.20.3 |

`libnccl.so.2.<major>.<minor>` gives the version, and the `NCCL_MAJOR`, `NCCL_MINOR` and `NCCL_PATCH` macros in `nccl.h` confirm it.

!!! tip "Check that the fabric path is wired up"
    With `NCCL_DEBUG=INFO`, NCCL prints the network plugin it selected at startup.
    This is the quickest confirmation that traffic will go over the fabric rather than a fallback.

## Environment variables

NCCL reads the `NCCL_*` family, which is listed under [Environment variables][ref-envvars-nccl].
For the netstack the ones that matter are `NCCL_NET_PLUGIN`, which selects [aws-ofi-nccl][ref-pkg-aws-ofi-nccl], along with `NCCL_NET` and `NCCL_DEBUG`.

## Related

* [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] is the libfabric and CXI transport plugin.
* [libfabric][ref-pkg-libfabric] is the fabric that NCCL ultimately runs over.
* [cuda][ref-pkg-cuda] provides the runtime that NCCL links.
