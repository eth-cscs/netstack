# nccl

> NVIDIA's collective communication library for multi-GPU / multi-node
> reductions, broadcasts and all-gathers.

|  |  |
|---|---|
| Spack package | `nccl` |
| Layer | GPU collectives |
| Provided by | **user** |
| User-buildable | yes |
| Slingshot component | via [aws-ofi-nccl][aws-ofi-nccl] → [libfabric][libfabric] |
| Upstream | <https://github.com/NVIDIA/nccl> |

## What it is

NCCL (`libnccl.so.2`) implements optimized primitives for collective multi-GPU
communication. Within a node it uses NVLink/PCIe directly; **across** nodes it
needs a network transport plugin. On Alps that plugin is
[aws-ofi-nccl][aws-ofi-nccl], which carries NCCL traffic over
[libfabric][libfabric]/CXI — so NCCL and MPI share the same Slingshot fabric.

## System vs. user

Always a **user** component: NCCL ships in the uenv (or a container / `pip`
wheel) and sits on the view path. It links the [CUDA runtime][cuda].

## Identifying it

The soname carries the full release, so `bin/user-stack` reads it directly:

| Environment | Version |
|---|---|
| `prgenv-gnu/25.11:v1` | 2.28.3 |
| `prgenv-gnu/25.6:v2`  | 2.27.5 |
| `prgenv-gnu/24.7:v3`  | 2.20.3 |

- `libnccl.so.2.<major>.<minor>` gives the version; the `NCCL_MAJOR/MINOR/PATCH`
  macros in `nccl.h` confirm it.
- With `NCCL_DEBUG=INFO`, NCCL prints the network plugin it selected at startup —
  the quickest check that the fabric path is wired up.

## Environment variables

The `NCCL_*` family — see [Environment variables][envvars]. For the netstack the
key ones are `NCCL_NET_PLUGIN` (selects [aws-ofi-nccl][aws-ofi-nccl]),
`NCCL_NET`, and `NCCL_DEBUG`.

## Related

- [aws-ofi-nccl][aws-ofi-nccl] — the libfabric/CXI transport plugin.
- [libfabric][libfabric] — the fabric it ultimately runs over.
- [cuda][cuda] — the runtime NCCL links.

[aws-ofi-nccl]: aws-ofi-nccl.md
[libfabric]: libfabric.md
[cuda]: cuda.md
[envvars]: ../envvars.md
