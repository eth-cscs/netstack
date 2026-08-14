# cray-pmi

> Cray's Process Management Interface — the library MPI uses to bootstrap a job:
> discover ranks, exchange addresses, wire up the fabric.

|  |  |
|---|---|
| Spack package | `cray-pmi` |
| Layer | launch / wire-up |
| Provided by | **user *or* system** |
| User-buildable | no — redistributed binary from HPE |
| Slingshot component | — |
| Upstream | <https://docs.nersc.gov/development/compilers/wrappers/> |

## What it is

`cray-pmi` provides `libpmi.so.0` and `libpmi2.so.0`, the PMI/PMI-2 client
libraries that [Cray MPICH][cray-mpich] links to bring a parallel job up: each
rank registers with the launcher, exchanges connection information, and only
then can the fabric be used. It is the control-plane sibling of the data-plane
([libfabric][libfabric]/[XPMEM][xpmem]).

At run time PMI talks to the launcher — [Slurm][slurm]'s PMI implementation under
`srun`, or [cray-pals][cray-pals] under `mpiexec`. The `PMI_*` environment
variables you see in a job are populated by that launcher.

## System vs. user

Commonly a **user** component (it ships in the uenv next to Cray MPICH), but the
system also provides PMI via the launcher. `bin/user-stack` resolves
`libpmi.so.0` via rpath from the MPI library and reports `cray-pmi` `6.1.15` in
all three reference uenvs.

## Identifying it

- `bin/user-stack` lists `cray-pmi` with its version and origin.
- The presence of `PMI_RANK`, `PMI_SIZE`, `PMI_CONTROL_PORT`, … in the
  environment confirms the wire-up path is active (these are set by the
  launcher, not by hand).

## Environment variables

The `PMI_*` family — launcher-populated identity/rendezvous. See
[Environment variables][envvars].

## Related

- [cray-mpich][cray-mpich] — the library that links PMI.
- [cray-pals][cray-pals] · [slurm][slurm] — the launchers PMI talks to.

[cray-mpich]: cray-mpich.md
[libfabric]: libfabric.md
[xpmem]: xpmem.md
[cray-pals]: cray-pals.md
[slurm]: slurm.md
[envvars]: ../envvars.md
