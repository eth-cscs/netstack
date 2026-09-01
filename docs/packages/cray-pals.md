[](){#ref-pkg-cray-pals}
# cray-pals

PALS, the HPE Cray Parallel Application Launch Service, is the `mpiexec` and `aprun` launcher.
It starts jobs and feeds [PMI][ref-pkg-cray-pmi] the job layout.

PALS is only usable with the PBS workload manager, and a such is not used or necessary on Alps.

| Property | Value |
|---|---|
| Spack package | `cray-pals` |
| Layer | Launch |
| Provided by | System. |
| User-buildable | No, it is a binary redistributed by HPE. |
| Slingshot component | No. |
| Upstream | HPE Cray PE. |

## What it is

PALS launches the ranks of a job, places them on nodes, and provides the runtime data that MPI needs in order to come up, namely the [PMI][ref-pkg-cray-pmi] wire-up and the per-rank identity.

## System or user

PALS is a user component, beacuse it is installed as a dependency of cray-mpich.

The pre-compiled cray-mpich binaries are linked against libpals, so it needs to be present, despite not being used or required.

## Identifying it

`PALS_RANKID`, `PALS_NODEID`, `PALS_APID` and `PALS_SPOOL_DIR` in the environment mean the job was launched by PALS.
The absence of those variables, together with the presence of only `PMI_*` and `SLURM_*`, means it was launched by Slurm instead.

## Environment variables

The `PALS_*` family is listed under [Environment variables][ref-envvars-launcher].

## Related

* [cray-pmi][ref-pkg-cray-pmi] is the wire-up library that PALS drives.
* [slurm][ref-pkg-slurm] is the alternative launcher.
