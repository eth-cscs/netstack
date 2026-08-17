[](){#ref-pkg-pmix}
# pmix

PMIx, the Process Management Interface for Exascale, is the launch and wire-up interface used by [Open MPI][ref-pkg-openmpi].
It is the counterpart to Cray MPICH's [cray-pmi][ref-pkg-cray-pmi].

| Property | Value |
|---|---|
| Spack package | `pmix`, often bundled inside [openmpi][ref-pkg-openmpi]. |
| Layer | Launch and wire-up |
| Provided by | User. |
| User-buildable | Yes. |
| Slingshot component | No. |
| Upstream | <https://openpmix.github.io/> |

## What it is

PMIx, as `libpmix.so`, is the successor to PMI and PMI-2.
It is the interface that an MPI runtime uses to bootstrap a job, by publishing and exchanging connection data, discovering ranks, and coordinating with the launcher, before the fabric can carry any traffic.
It is the control-plane counterpart to the data plane, which is made up of [libfabric][ref-pkg-libfabric] and [XPMEM][ref-pkg-xpmem].

At run time PMIx connects to the PMIx server of the launcher, which is either the one embedded in Slurm for `srun --mpi=pmix`, or the one in Open MPI's own PRRTE for `mpirun`.

## System or user

PMIx is a user component.
In `prgenv-gnu-openmpi` it ships inside the Open MPI package, with `libpmix.so.2` living in the `openmpi-*` store prefix, so [`user-stack`][ref-tools-user-stack] attributes it to the Spack hash of Open MPI.
It can also be installed as a standalone `pmix` package.

## Identifying it

[`user-stack`][ref-tools-user-stack] reports `pmix` whenever `libpmix.so` is on the view path, which is the signal that the MPI stack uses PMIx rather than Cray PMI.

| Environment | Version (soname) | Origin |
|---|---|---|
| `prgenv-gnu-openmpi/26.3:v1` | 2.13.10 | uenv |

As with [libcxi][ref-pkg-libcxi], the soname version, from `libpmix.so.2.13.10`, is the shared-object version, and it differs from the PMIx release number.
See [version namespaces][ref-analysis-uenv-version-namespaces].

## Environment variables

The `PMIX_*` family is mostly populated by the launcher, and covers the server URI, the rank and the namespace.
It is listed under [Environment variables][ref-envvars-launcher].

## Related

* [openmpi][ref-pkg-openmpi] is the MPI that uses PMIx here.
* [cray-pmi][ref-pkg-cray-pmi] is the Cray MPICH equivalent.
* [slurm][ref-pkg-slurm] provides a PMIx server for `srun`.
