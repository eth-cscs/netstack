[](){#ref-pkg-cray-gtl}
# cray-gtl

The Cray GPU Transport Layer makes [Cray MPICH][ref-pkg-cray-mpich] GPU-aware. MPI calls can then take device pointers.

| Property | Value |
|---|---|
| Spack package | `cray-gtl` |
| Layer | GPU-aware MPI |
| Provided by | User, shipped with Cray MPICH. |
| User-buildable | No, it is a binary redistributed by HPE. |
| Slingshot component | No. |
| Upstream | HPE Cray PE, distributed with Cray MPICH. |

## What it is

`cray-gtl` provides `libmpi_gtl_cuda.so`. This is the glue that lets [Cray MPICH][ref-pkg-cray-mpich] accept GPU device pointers in MPI calls.
It also moves that data over the fabric or through GPU IPC, without an explicit staging copy through host memory.
MPICH loads it only when you switch on GPU support with `MPICH_GPU_SUPPORT_ENABLED=1`.

The library name shows that it is CUDA-specific. It links the [CUDA runtime][ref-pkg-cuda] and the CUDA driver.
Its version tracks the version of Cray MPICH.

## System or user

`cray-gtl` is a user component.
It is part of the Cray MPICH distribution, and it lives on the view path next to Cray MPICH.

On its own it does nothing.
It needs [Cray MPICH][ref-pkg-cray-mpich] above it, and the [CUDA][ref-pkg-cuda] runtime and driver below it.

## Identifying it

If `libmpi_gtl_cuda.so` is present in the view, and the MPI library links it, this confirms that GPU-aware MPI is available.
[`user-stack`][ref-tools-user-stack] reports `cray-gtl`, found through an rpath from the MPI library.

| Environment | Version |
|---|---|
| `prgenv-gnu/25.11:v1` | 8.1.32 |
| `prgenv-gnu/25.6:v2` | 8.1.32 |
| `prgenv-gnu/24.7:v3` | 8.1.30 |

!!! note "Available is not the same as active"
    GPU-awareness is only in use if `MPICH_GPU_SUPPORT_ENABLED` is also set at run time.

## Environment variables

`MPICH_GPU_SUPPORT_ENABLED` is the master switch that MPICH reads to enable the GTL. `MPICH_GPU_IPC_ENABLED` controls intra-node GPU-to-GPU transfers through CUDA IPC.
[Environment variables][ref-envvars-mpich] lists both.

## Related

* [cray-mpich][ref-pkg-cray-mpich] is the MPI that loads this layer.
* [cuda][ref-pkg-cuda] provides the runtime and driver that the GTL links.
