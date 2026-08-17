[](){#ref-pkg-cray-pals}
# cray-pals

PALS, the HPE Cray Parallel Application Launch Service, is the `mpiexec` and `aprun` launcher.
It starts jobs and feeds [PMI][ref-pkg-cray-pmi] the job layout.

| Property | Value |
|---|---|
| Spack package | `cray-pals` |
| Layer | Launch |
| Provided by | System. |
| User-buildable | No, it is a binary redistributed by HPE. |
| Slingshot component | No. |
| Upstream | HPE Cray PE. |

## What it is

PALS launches the ranks of a job, places them on nodes, and provides the runtime data that MPI needs in order to come up, which is the [PMI][ref-pkg-cray-pmi] wire-up and the per-rank identity.
On Alps it is the launcher behind `mpiexec`.
When jobs are started with [Slurm][ref-pkg-slurm] and `srun`, the Slurm launcher and its PMI take that role instead.

Its footprint at run time is the `PALS_*` environment variables that it exports, covering the rank id, node id, application id and spool directory, and, where present, `libpals`.

## System or user

PALS is a system component, part of the host launcher stack rather than of the uenv.

In the reference `prgenv-gnu` uenvs, [`user-stack`][ref-tools-user-stack] reports `cray-pals` as absent from the view.
That is correct, because no PALS library is on the view path.
The `PALS_*` variables are still injected by the launcher when a job runs under it.

## Identifying it

`PALS_RANKID`, `PALS_NODEID`, `PALS_APID` and `PALS_SPOOL_DIR` in the environment mean the job was launched by PALS.
The absence of those variables, together with the presence of only `PMI_*` and `SLURM_*`, means it was launched by Slurm instead.

## Environment variables

The `PALS_*` family is listed under [Environment variables][ref-envvars-launcher].

## Related

* [cray-pmi][ref-pkg-cray-pmi] is the wire-up library that PALS drives.
* [slurm][ref-pkg-slurm] is the alternative launcher.
