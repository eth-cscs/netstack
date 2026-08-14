# openmpi

> Open MPI — an alternative MPI implementation that also runs over
> [libfabric][libfabric]/CXI on Slingshot.

|  |  |
|---|---|
| Spack package | `openmpi` |
| Layer | MPI |
| Provided by | **user** |
| User-buildable | yes |
| Slingshot component | via [libfabric][libfabric] (OFI MTL/BTL) |
| Upstream | <https://www.open-mpi.org> |

## What it is

Open MPI is an independent, community-developed MPI implementation. It is **not**
ABI-compatible with MPICH/Cray MPICH — an application must be built and run
against the same family. On Alps it reaches Slingshot through its OFI component,
i.e. through the same [libfabric][libfabric] `cxi` provider that Cray MPICH uses.

Open MPI is packaged in dedicated environments such as
`prgenv-gnu-openmpi`; the standard `prgenv-gnu` uses [Cray MPICH][cray-mpich].

## System vs. user

Always a **user** component. Its netstack dependencies ([libfabric][libfabric],
[libcxi][libcxi], [xpmem][xpmem], [cuda][cuda]) follow the same system-vs-user
rules as for Cray MPICH — check provenance per environment with the tools.

## Identifying it

`bin/user-stack` is MPI-flavour aware: it resolves the MPI library to its Spack
store directory (`openmpi-*` vs `cray-mpich-*` vs `mpich-*`) and reports the
right implementation. For an Open MPI stack it emits an `openmpi` row (version
from `ompi_info --version`) and, in place of the Cray-specific
[cray-gtl][cray-gtl] / [cray-pmi][cray-pmi] / [cray-pals][cray-pals] rows, a
[pmix][pmix] process-management row. Example (`prgenv-gnu-openmpi/26.3:v1`):

| Component | Version | Origin | Role |
|---|---|---|---|
| openmpi | 5.0.10 | uenv | MPI (Open MPI) |
| libfabric | 2.3.1 | uenv | OFI fabric abstraction |
| libcxi | 1.5.0 | uenv | Slingshot (CXI) user-space library |
| nccl | 2.29.2 | uenv | GPU collectives |
| aws-ofi-nccl | 1.17.2 | uenv | NCCL ↔ libfabric transport plugin |
| cuda | 13.1.1 | uenv | CUDA runtime (toolkit) |
| pmix | 2.13.10 | uenv | process management interface (PMIx) |

Other tells: the MPI library is `libmpi.so.40` (Open MPI) rather than
`libmpi_*.so.12` (Cray MPICH), and `ompi_info` lists the MCA components — look
for the `ofi` MTL/BTL (Slingshot via libfabric) and the `cuda` accelerator
(GPU-aware without a GTL).

## Environment variables

Open MPI is configured through `OMPI_*` / MCA parameters rather than `MPICH_*`,
and its launch through `PMIX_*` ([pmix][pmix]). The fabric-level `FI_*` variables
([libfabric][libfabric]) still apply. See [Environment variables][envvars].

## Related

- [cray-mpich][cray-mpich] · [mpich][mpich] — the MPICH family.
- [pmix][pmix] — the launch/wire-up interface Open MPI uses.
- [libfabric][libfabric] — the shared fabric layer.

[cray-mpich]: cray-mpich.md
[mpich]: mpich.md
[pmix]: pmix.md
[cray-gtl]: cray-gtl.md
[cray-pmi]: cray-pmi.md
[cray-pals]: cray-pals.md
[libfabric]: libfabric.md
[libcxi]: libcxi.md
[xpmem]: xpmem.md
[cuda]: cuda.md
[envvars]: ../envvars.md
