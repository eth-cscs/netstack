[](){#ref-pkg-cray-pmi}
# cray-pmi

`cray-pmi` is Cray's Process Management Interface. MPI uses this library to start a job. It discovers the ranks, exchanges addresses, and connects the fabric.

| Property | Value |
|---|---|
| Spack package | `cray-pmi` |
| Layer | Launch and wire-up |
| Provided by | User or system. |
| User-buildable | No. HPE redistributes it as a binary. |
| Slingshot component | No. |
| Upstream | <https://docs.nersc.gov/development/compilers/wrappers/> |

## What it is

`cray-pmi` provides `libpmi.so.0` and `libpmi2.so.0`. These are the PMI and PMI-2 client libraries. [Cray MPICH][ref-pkg-cray-mpich] links them to start a parallel job.
Each rank registers with the launcher and exchanges connection information. Only after this step can the job use the fabric.
PMI is the control-plane sibling of the data plane. [libfabric][ref-pkg-libfabric] and [XPMEM][ref-pkg-xpmem] make up the data plane.

At run time, PMI talks to the launcher. Under `srun`, this is the PMI implementation in [Slurm][ref-pkg-slurm]. Under `mpiexec`, this is [cray-pals][ref-pkg-cray-pals].
The launcher sets the `PMI_*` variables visible in a job.

## System or user

`cray-pmi` is usually a user component, because it ships in the uenv next to Cray MPICH. But the system also provides PMI through the launcher.
[`user-stack`][ref-tools-user-stack] resolves `libpmi.so.0` through an rpath from the MPI library. It reports `cray-pmi` version `6.1.15` in all three reference uenvs.

## Identifying it

[`user-stack`][ref-tools-user-stack] lists `cray-pmi` with its version and origin.
If `PMI_RANK`, `PMI_SIZE` and `PMI_CONTROL_PORT` are present in the environment, the wire-up path is active. The launcher sets these variables; a user does not set them by hand.

## Environment variables

The launcher sets the `PMI_*` family with identity and rendezvous information. [Environment variables][ref-envvars-launcher] lists this family.

## Related

* [cray-mpich][ref-pkg-cray-mpich] is the library that links PMI.
* [cray-pals][ref-pkg-cray-pals] and [slurm][ref-pkg-slurm] are the launchers that PMI talks to.
* [pmix][ref-pkg-pmix] is the equivalent used by Open MPI.
