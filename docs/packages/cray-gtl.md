[](){#ref-pkg-cray-gtl}
# cray-gtl

The Cray GPU Transport Layer makes [Cray MPICH][ref-pkg-cray-mpich] GPU-aware, so that MPI calls can be given device pointers.

| Property | Value |
|---|---|
| Spack package | `cray-gtl` |
| Layer | GPU-aware MPI |
| Provided by | User, shipped with Cray MPICH. |
| User-buildable | No, it is a binary redistributed by HPE. |
| Slingshot component | No. |
| Upstream | HPE Cray PE, distributed with Cray MPICH. |

## What it is

`cray-gtl` provides `libmpi_gtl_cuda.so`, the glue that lets [Cray MPICH][ref-pkg-cray-mpich] accept GPU device pointers in MPI calls, and move that data over the fabric or through GPU IPC without an explicit staging copy through host memory.
MPICH loads it only when GPU support is switched on with `MPICH_GPU_SUPPORT_ENABLED=1`.

The library is CUDA-specific, as its name says, and it links the [CUDA runtime][ref-pkg-cuda] and the CUDA driver.
Its version tracks the version of Cray MPICH.

## System or user

`cray-gtl` is a user component.
It is part of the Cray MPICH distribution and lives on the view path next to it.

On its own it does nothing.
It needs [Cray MPICH][ref-pkg-cray-mpich] above it and the [CUDA][ref-pkg-cuda] runtime and driver below it.

## Identifying it

`libmpi_gtl_cuda.so` being present in the view, and being linked by the MPI library, confirms that GPU-aware MPI is available.
[`user-stack`][ref-tools-user-stack] reports `cray-gtl`, found through an rpath from the MPI library.

| Environment | Version |
|---|---|
| `prgenv-gnu/25.11:v1` | 8.1.32 |
| `prgenv-gnu/25.6:v2` | 8.1.32 |
| `prgenv-gnu/24.7:v3` | 8.1.30 |

!!! note "Available is not the same as active"
    Whether GPU-awareness is actually in use additionally depends on `MPICH_GPU_SUPPORT_ENABLED` being set at run time.

## Environment variables

`MPICH_GPU_SUPPORT_ENABLED` is the master switch, read by MPICH, that enables the GTL, and `MPICH_GPU_IPC_ENABLED` controls intra-node GPU-to-GPU transfers through CUDA IPC.
Both are listed under [Environment variables][ref-envvars-mpich].

## Related

* [cray-mpich][ref-pkg-cray-mpich] is the MPI that loads this layer.
* [cuda][ref-pkg-cuda] provides the runtime and driver that the GTL links.
