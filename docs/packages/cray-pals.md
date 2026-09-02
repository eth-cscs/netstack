[](){#ref-pkg-cray-pals}
# cray-pals

PALS, the HPE Cray Parallel Application Launch Service, is the `mpiexec` and `aprun` launcher.
It starts jobs and feeds [PMI][ref-pkg-cray-pmi] the job layout.

PALS only works with the PBS workload manager. Alps does not use PBS, so Alps does not need PALS.

| Property | Value |
|---|---|
| Spack package | `cray-pals` |
| Layer | Launch |
| Provided by | System. |
| User-buildable | No, it is a binary redistributed by HPE. |
| Slingshot component | No. |
| Upstream | HPE Cray PE. |

## What it is

PALS launches the ranks of a job and places them on nodes.
It also gives MPI the runtime data MPI must have to start, namely the [PMI][ref-pkg-cray-pmi] wire-up and the per-rank identity.

## System or user

PALS is a user component, because it is a dependency of cray-mpich.

The pre-compiled cray-mpich binaries link against libpals. PALS must therefore be present, even though nothing uses it or requires it.

## Identifying it

If `PALS_RANKID`, `PALS_NODEID`, `PALS_APID` and `PALS_SPOOL_DIR` are present in the environment, PALS launched the job.
If those variables are absent, and only `PMI_*` and `SLURM_*` are present, Slurm launched the job instead.

## Environment variables

[Environment variables][ref-envvars-launcher] lists the `PALS_*` family.

## Related

* [cray-pmi][ref-pkg-cray-pmi] is the wire-up library that PALS drives.
* [slurm][ref-pkg-slurm] is the alternative launcher.
