# cray-gtl

> Cray's **GPU Transport Layer** — the component that makes [Cray MPICH][cray-mpich]
> GPU-aware, letting MPI calls pass device pointers directly.

|  |  |
|---|---|
| Spack package | `cray-gtl` |
| Layer | GPU-aware MPI |
| Provided by | **user** (ships with Cray MPICH) |
| User-buildable | no — redistributed binary from HPE |
| Slingshot component | — |
| Upstream | (HPE Cray PE, distributed with Cray MPICH) |

## What it is

`cray-gtl` provides `libmpi_gtl_cuda.so`, the glue that lets [Cray
MPICH][cray-mpich] accept **GPU (device) pointers** in MPI calls and move that
data over the fabric or via GPU IPC without an explicit host staging copy. It is
loaded by MPICH only when GPU support is switched on with
`MPICH_GPU_SUPPORT_ENABLED=1`.

The library is CUDA-specific (`_gtl_cuda`); it links the [CUDA runtime][cuda] and
the CUDA driver. Its version tracks Cray MPICH.

## System vs. user

A **user** component: it is part of the Cray MPICH distribution and lives on the
view path next to it. On its own it does nothing — it needs both
[Cray MPICH][cray-mpich] above and the [CUDA][cuda] runtime/driver below.

## Identifying it

- Presence of `libmpi_gtl_cuda.so` in the view, and it being linked by the MPI
  library, confirms GPU-aware MPI is *available*.
- `bin/user-stack` reports `cray-gtl` (found via **rpath** from the MPI library):

| Environment | Version |
|---|---|
| `prgenv-gnu/25.11:v1` | 8.1.32 |
| `prgenv-gnu/25.6:v2`  | 8.1.32 |
| `prgenv-gnu/24.7:v3`  | 8.1.30 |

- Whether GPU-awareness is *active* additionally depends on
  `MPICH_GPU_SUPPORT_ENABLED`.

## Environment variables

- `MPICH_GPU_SUPPORT_ENABLED` — the master switch (read by MPICH, enables GTL).
- `MPICH_GPU_IPC_ENABLED` — intra-node GPU↔GPU via CUDA IPC.

See [Environment variables][envvars].

## Related

- [cray-mpich][cray-mpich] — the MPI that loads this layer.
- [cuda][cuda] — the runtime/driver GTL links.

[cray-mpich]: cray-mpich.md
[cuda]: cuda.md
[envvars]: ../envvars.md
