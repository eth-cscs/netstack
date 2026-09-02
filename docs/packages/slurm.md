[](){#ref-pkg-slurm}
# slurm

Slurm is the workload manager.
In the netstack it matters as a launcher, because `srun` starts the ranks and provides the [PMI][ref-pkg-cray-pmi] wire-up.

| Property | Value |
|---|---|
| Spack package | `slurm` |
| Layer | Launch |
| Provided by | System. |
| User-buildable | No. The site manages it. |
| Slingshot component | No. |
| Upstream | <https://slurm.schedmd.com/> |

## What it is

Slurm schedules jobs and, through `srun`, launches the processes of a parallel job.
Its relevant job for the netstack is process management. `srun` places ranks on nodes. `srun` also speaks PMI and PMI-2 to bootstrap MPI. It exchanges the information each rank needs before the ranks can use the fabric.
It is one of the two launch paths on Alps. The other is [cray-pals][ref-pkg-cray-pals] under `mpiexec`.

Slurm does not move application data. That is the job of the fabric: [libfabric][ref-pkg-libfabric] and [XPMEM][ref-pkg-xpmem].
Slurm matters here because a wire-up that uses the wrong PMI, or a mismatched PMI, causes a genuine netstack failure.

## System or user

Slurm is always a system component. The site installs and manages it.
The RPM is `slurm`, version `25.5.4` on the reference node. [`system-stack`][ref-tools-system-stack] reports it.

## Identifying it

`SLURM_*` environment variables in a job show that Slurm launched it.

```console title="Listing the PMI plugins that Slurm can provide"
$ srun --mpi=list
```

[`system-stack`][ref-tools-system-stack] reports the installed Slurm version.

## Related

* [cray-pmi][ref-pkg-cray-pmi] provides the PMI libraries that the launcher drives.
* [pmix][ref-pkg-pmix] is the PMIx interface that Slurm can also serve.
* [cray-pals][ref-pkg-cray-pals] is the alternative, Cray, launcher.
