[](){#ref-pkg-pmix}
# pmix

PMIx, the Process Management Interface for Exascale, is the launch and wire-up interface that [Open MPI][ref-pkg-openmpi] uses.
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
It is the interface that an MPI runtime uses to bootstrap a job. Before the fabric can carry any traffic, PMIx publishes and exchanges connection data, discovers ranks, and coordinates with the launcher.
It is the control-plane counterpart to the data plane. [libfabric][ref-pkg-libfabric] and [XPMEM][ref-pkg-xpmem] make up the data plane.

At run time, PMIx connects to the PMIx server of the launcher. For `srun --mpi=pmix`, this is the server embedded in Slurm. For `mpirun`, this is the server in Open MPI's own PRRTE.

## System or user

PMIx is a user component.
In `prgenv-gnu-openmpi`, it ships inside the Open MPI package. `libpmix.so.2` lives in the `openmpi-*` store prefix. Because of this, [`user-stack`][ref-tools-user-stack] attributes it to the Spack hash of Open MPI.
You can also install it as a standalone `pmix` package.

## Identifying it

[`user-stack`][ref-tools-user-stack] reports `pmix` whenever `libpmix.so` is on the view path. This is the signal that the MPI stack uses PMIx rather than Cray PMI.

| Environment | Version (soname) | Origin |
|---|---|---|
| `prgenv-gnu-openmpi/26.3:v1` | 2.13.10 | uenv |

As with [libcxi][ref-pkg-libcxi], the soname version, from `libpmix.so.2.13.10`, is the shared-object version. It differs from the PMIx release number.
See [version namespaces][ref-analysis-uenv-version-namespaces].

## Environment variables

The launcher populates most of the `PMIX_*` family. It covers the server URI, the rank and the namespace.
[Environment variables][ref-envvars-launcher] lists it.

## Related

* [openmpi][ref-pkg-openmpi] is the MPI that uses PMIx here.
* [cray-pmi][ref-pkg-cray-pmi] is the Cray MPICH equivalent.
* [slurm][ref-pkg-slurm] provides a PMIx server for `srun`.
