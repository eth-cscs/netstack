[](){#ref-pkg-openmpi}
# openmpi

Open MPI is an alternative MPI implementation, which also runs over [libfabric][ref-pkg-libfabric] and the CXI provider on Slingshot.

| Property | Value |
|---|---|
| Spack package | `openmpi` |
| Layer | MPI |
| Provided by | User. |
| User-buildable | Yes. |
| Slingshot component | Indirectly, through [libfabric][ref-pkg-libfabric] and the OFI MTL or BTL. |
| Upstream | <https://www.open-mpi.org> |

## What it is

Open MPI is an independent, community-developed MPI implementation.
On Alps it reaches Slingshot through its OFI component, which means through the same [libfabric][ref-pkg-libfabric] `cxi` provider that Cray MPICH uses.

Open MPI is packaged in dedicated environments such as `prgenv-gnu-openmpi`, while the standard `prgenv-gnu` uses [Cray MPICH][ref-pkg-cray-mpich].

!!! warning "Open MPI is not ABI-compatible with MPICH"
    Unlike [mpich][ref-pkg-mpich] and [cray-mpich][ref-pkg-cray-mpich], which share an ABI, an application has to be built and run against the same MPI family as Open MPI.

## System or user

Open MPI is always a user component.

Its netstack dependencies, which are [libfabric][ref-pkg-libfabric], [libcxi][ref-pkg-libcxi], [xpmem][ref-pkg-xpmem] and [cuda][ref-pkg-cuda], follow the same system or user rules as they do for Cray MPICH, so check their provenance per environment with the [tools][ref-tools].

## Identifying it

[`user-stack`][ref-tools-user-stack] is MPI-flavour aware.
It resolves the MPI library to its Spack store directory, distinguishing `openmpi-*` from `cray-mpich-*` and `mpich-*`, and reports the matching implementation.
For an Open MPI stack it emits an `openmpi` row, with the version taken from `ompi_info --version`, and in place of the Cray-specific [cray-gtl][ref-pkg-cray-gtl], [cray-pmi][ref-pkg-cray-pmi] and [cray-pals][ref-pkg-cray-pals] rows it emits a [pmix][ref-pkg-pmix] row.

!!! example "Output for `prgenv-gnu-openmpi/26.3:v1`"
    | Component | Version | Origin | Role |
    |---|---|---|---|
    | openmpi | 5.0.10 | uenv | MPI (Open MPI) |
    | libfabric | 2.3.1 | uenv | OFI fabric abstraction |
    | libcxi | 1.5.0 | uenv | Slingshot (CXI) user-space library |
    | nccl | 2.29.2 | uenv | GPU collectives |
    | aws-ofi-nccl | 1.17.2 | uenv | NCCL to libfabric transport plugin |
    | cuda | 13.1.1 | uenv | CUDA runtime (toolkit) |
    | pmix | 2.13.10 | uenv | Process management interface (PMIx) |

There are two other tells.
The MPI library is `libmpi.so.40` for Open MPI, rather than `libmpi_*.so.12` for Cray MPICH.
And `ompi_info` lists the MCA components, where you should look for the `ofi` MTL or BTL, which is Slingshot through libfabric, and the `cuda` accelerator, which gives GPU-awareness without a GTL.

## Environment variables

Open MPI is configured through `OMPI_*` variables and MCA parameters rather than through `MPICH_*`, and its launch through `PMIX_*`.
The fabric-level `FI_*` variables still apply.
All three families are listed under [Environment variables][ref-envvars-openmpi].

## Related

* [cray-mpich][ref-pkg-cray-mpich] and [mpich][ref-pkg-mpich] are the MPICH family.
* [pmix][ref-pkg-pmix] is the launch and wire-up interface that Open MPI uses.
* [libfabric][ref-pkg-libfabric] is the fabric layer shared with Cray MPICH.
