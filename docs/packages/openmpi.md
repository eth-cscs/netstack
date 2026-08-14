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

- `ompi_info` prints the Open MPI version and the MCA components (look for the
  `ofi` MTL / BTL and `cuda` support).
- The MPI library is `libmpi.so.40` (Open MPI) rather than `libmpi_*.so.12`
  (Cray MPICH); the resolved Spack store directory is `openmpi-*`.

!!! note
    `bin/user-stack` currently keys its MPI detection on the Cray MPICH
    libraries and `mpichversion`. In an Open MPI environment it will fall back to
    a generic `mpi` row; the fabric layers below (libfabric, libcxi, …) are still
    reported correctly.

## Environment variables

Open MPI is configured through `OMPI_*` / MCA parameters rather than `MPICH_*`.
The fabric-level `FI_*` variables ([libfabric][libfabric]) still apply.

## Related

- [cray-mpich][cray-mpich] · [mpich][mpich] — the MPICH family.
- [libfabric][libfabric] — the shared fabric layer.

[cray-mpich]: cray-mpich.md
[mpich]: mpich.md
[libfabric]: libfabric.md
[libcxi]: libcxi.md
[xpmem]: xpmem.md
[cuda]: cuda.md
