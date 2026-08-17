[](){#ref-pkg-cray-pmi}
# cray-pmi

`cray-pmi` is Cray's Process Management Interface, the library that MPI uses to bootstrap a job: discover the ranks, exchange addresses, and wire up the fabric.

| Property | Value |
|---|---|
| Spack package | `cray-pmi` |
| Layer | Launch and wire-up |
| Provided by | User or system. |
| User-buildable | No, it is a binary redistributed by HPE. |
| Slingshot component | No. |
| Upstream | <https://docs.nersc.gov/development/compilers/wrappers/> |

## What it is

`cray-pmi` provides `libpmi.so.0` and `libpmi2.so.0`, the PMI and PMI-2 client libraries that [Cray MPICH][ref-pkg-cray-mpich] links in order to bring a parallel job up.
Each rank registers with the launcher and exchanges connection information, and only then can the fabric be used.
PMI is the control-plane sibling of the data plane, which is made up of [libfabric][ref-pkg-libfabric] and [XPMEM][ref-pkg-xpmem].

At run time PMI talks to the launcher, either the PMI implementation in [Slurm][ref-pkg-slurm] under `srun`, or [cray-pals][ref-pkg-cray-pals] under `mpiexec`.
The `PMI_*` variables visible in a job are populated by that launcher.

## System or user

`cray-pmi` is commonly a user component, because it ships in the uenv next to Cray MPICH, but the system also provides PMI through the launcher.
[`user-stack`][ref-tools-user-stack] resolves `libpmi.so.0` through an rpath from the MPI library, and reports `cray-pmi` version `6.1.15` in all three reference uenvs.

## Identifying it

[`user-stack`][ref-tools-user-stack] lists `cray-pmi` with its version and origin.
The presence of `PMI_RANK`, `PMI_SIZE` and `PMI_CONTROL_PORT` in the environment confirms that the wire-up path is active, and those are set by the launcher rather than by hand.

## Environment variables

The `PMI_*` family holds launcher-populated identity and rendezvous information, and is listed under [Environment variables][ref-envvars-launcher].

## Related

* [cray-mpich][ref-pkg-cray-mpich] is the library that links PMI.
* [cray-pals][ref-pkg-cray-pals] and [slurm][ref-pkg-slurm] are the launchers that PMI talks to.
* [pmix][ref-pkg-pmix] is the equivalent used by Open MPI.
