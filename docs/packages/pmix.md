# pmix

> The Process Management Interface — Exascale. The launch / wire-up interface
> used by [Open MPI][openmpi] (the PMIx counterpart to Cray MPICH's
> [cray-pmi][cray-pmi]).

|  |  |
|---|---|
| Spack package | `pmix` (often bundled inside [openmpi][openmpi]) |
| Layer | launch / wire-up |
| Provided by | **user** |
| User-buildable | yes |
| Slingshot component | — |
| Upstream | <https://openpmix.github.io/> |

## What it is

PMIx (`libpmix.so`) is the modern successor to PMI/PMI-2: the interface an MPI
runtime uses to bootstrap a job — publish and exchange connection data, discover
ranks, and coordinate with the launcher — before the fabric can carry traffic.
It is the control-plane counterpart to the data-plane ([libfabric][libfabric] /
[XPMEM][xpmem]), and for [Open MPI][openmpi] it plays the role that
[cray-pmi][cray-pmi] plays for [Cray MPICH][cray-mpich].

At run time PMIx connects to the launcher's PMIx server — the one embedded in
Slurm (`srun --mpi=pmix`) or in Open MPI's own PRRTE (`mpirun`).

## System vs. user

A **user** component. In `prgenv-gnu-openmpi` it ships **inside** the Open MPI
package (`libpmix.so.2` lives in the `openmpi-*` store prefix), so `user-stack`
attributes it to Open MPI's Spack hash. It can also be a standalone `pmix`
package.

## Identifying it

`bin/user-stack` reports `pmix` whenever `libpmix.so` is on the view path — which
is the signal that the MPI stack uses PMIx rather than Cray PMI:

| Environment | Version (soname) | Origin |
|---|---|---|
| `prgenv-gnu-openmpi/26.3:v1` | 2.13.10 | uenv |

As with [libcxi][libcxi], the soname version (`libpmix.so.2.13.10`) is the
shared-object version, which differs from the PMIx release number.

## Environment variables

The `PMIX_*` family — mostly launcher-populated (server URI, rank, namespace).
See [Environment variables][envvars].

## Related

- [openmpi][openmpi] — the MPI that uses PMIx here.
- [cray-pmi][cray-pmi] — the Cray MPICH equivalent.
- [slurm][slurm] — provides a PMIx server for `srun`.

[openmpi]: openmpi.md
[cray-pmi]: cray-pmi.md
[cray-mpich]: cray-mpich.md
[libfabric]: libfabric.md
[libcxi]: libcxi.md
[xpmem]: xpmem.md
[slurm]: slurm.md
[envvars]: ../envvars.md
