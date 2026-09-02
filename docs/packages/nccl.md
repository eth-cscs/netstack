[](){#ref-pkg-nccl}
# nccl

NCCL is NVIDIA's collective communication library. Applications use it for multi-GPU and multi-node reductions, broadcasts and all-gathers.

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
Across nodes, it needs a network transport plugin. On Alps, that plugin is [aws-ofi-nccl][ref-pkg-aws-ofi-nccl]. It carries NCCL traffic over [libfabric][ref-pkg-libfabric] and the CXI provider.
NCCL and MPI therefore share the same Slingshot fabric.

## System or user

NCCL is always a user component.
It ships in the uenv, in a container, or in a `pip` wheel. It sits on the view path.
It links the [CUDA runtime][ref-pkg-cuda].

## Identifying it

The soname carries the full release. [`user-stack`][ref-tools-user-stack] reads the version from it directly.

| Environment | Version |
|---|---|
| `prgenv-gnu/25.11:v1` | 2.28.3 |
| `prgenv-gnu/25.6:v2` | 2.27.5 |
| `prgenv-gnu/24.7:v3` | 2.20.3 |

`libnccl.so.2.<major>.<minor>` gives the version. The `NCCL_MAJOR`, `NCCL_MINOR` and `NCCL_PATCH` macros in `nccl.h` confirm it.

!!! tip "Check that the fabric path is wired up"
    With `NCCL_DEBUG=INFO`, NCCL prints the network plugin it selected at startup.
    This is the fastest way to confirm that traffic goes over the fabric and not a fallback.

## Environment variables

NCCL reads the `NCCL_*` family of variables. See [Environment variables][ref-envvars-nccl] for the full list.
For the netstack, the important variables are `NCCL_NET_PLUGIN`, `NCCL_NET` and `NCCL_DEBUG`. `NCCL_NET_PLUGIN` selects [aws-ofi-nccl][ref-pkg-aws-ofi-nccl].

## Related

* [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] is the libfabric and CXI transport plugin.
* [libfabric][ref-pkg-libfabric] is the fabric that NCCL ultimately runs over.
* [cuda][ref-pkg-cuda] provides the runtime that NCCL links.
