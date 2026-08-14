# cray-pals

> The HPE Cray **Parallel Application Launch Service** — the `mpiexec`/`aprun`
> launcher that starts jobs and feeds [PMI][cray-pmi] the job layout.

|  |  |
|---|---|
| Spack package | `cray-pals` |
| Layer | launch |
| Provided by | **system** |
| User-buildable | no — redistributed binary from HPE |
| Slingshot component | — |
| Upstream | (HPE Cray PE) |

## What it is

PALS is the Cray application launch service. It launches the ranks of a job,
places them on nodes, and provides the runtime data ([PMI][cray-pmi] wire-up,
per-rank identity) that MPI needs to come up. On Alps it is the launcher behind
`mpiexec`; when jobs are started with [Slurm][slurm]'s `srun`, Slurm's own
launcher/PMI takes that role instead.

Its footprint at run time is the `PALS_*` environment variables it exports
(rank id, node id, application id, spool directory) and, where present,
`libpals`.

## System vs. user

A **system** component: it is part of the host launcher stack, not the uenv. In
the reference prgenv-gnu uenvs `bin/user-stack` reports `cray-pals` as
**absent** from the view — correctly, because no PALS *library* is on the view
path; the `PALS_*` variables are still injected by the launcher when a job runs
under it.

## Identifying it

- `PALS_RANKID`, `PALS_NODEID`, `PALS_APID`, `PALS_SPOOL_DIR`, … in the
  environment ⇒ the job was launched by PALS.
- Absence of these (and presence of only `PMI_*` / `SLURM_*`) ⇒ launched by
  Slurm instead.

## Environment variables

The `PALS_*` family — see [Environment variables][envvars].

## Related

- [cray-pmi][cray-pmi] — the wire-up library PALS drives.
- [slurm][slurm] — the alternative launcher.

[cray-pmi]: cray-pmi.md
[slurm]: slurm.md
[envvars]: ../envvars.md
