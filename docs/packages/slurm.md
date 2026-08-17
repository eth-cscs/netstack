[](){#ref-pkg-slurm}
# slurm

Slurm is the workload manager.
In the netstack it matters as a launcher, because `srun` starts the ranks and provides the [PMI][ref-pkg-cray-pmi] wire-up.

| Property | Value |
|---|---|
| Spack package | `slurm` |
| Layer | Launch |
| Provided by | System. |
| User-buildable | No, it is managed by the site. |
| Slingshot component | No. |
| Upstream | <https://slurm.schedmd.com/> |

## What it is

Slurm schedules jobs and, through `srun`, launches the processes of a parallel job.
Its relevant job for the netstack is process management: `srun` places ranks on nodes and speaks PMI and PMI-2 to bootstrap MPI, exchanging the information each rank needs before the fabric can be used.
It is one of the two launch paths on Alps, the other being [cray-pals][ref-pkg-cray-pals] under `mpiexec`.

Slurm does not move application data, because that is the job of the fabric, meaning [libfabric][ref-pkg-libfabric] and [XPMEM][ref-pkg-xpmem].
It is part of the picture because a wire-up handled by the wrong or a mismatched PMI is a genuine netstack failure mode.

## System or user

Slurm is always a system component, installed and managed by the site.
The RPM is `slurm`, version `25.5.4` on the reference node, and [`system-stack`][ref-tools-system-stack] reports it.

## Identifying it

`SLURM_*` environment variables in a job mean it was launched under Slurm.

```console title="Listing the PMI plugins that Slurm can provide"
$ srun --mpi=list
```

[`system-stack`][ref-tools-system-stack] reports the installed Slurm version.

## Related

* [cray-pmi][ref-pkg-cray-pmi] provides the PMI libraries that the launcher drives.
* [pmix][ref-pkg-pmix] is the PMIx interface that Slurm can also serve.
* [cray-pals][ref-pkg-cray-pals] is the alternative, Cray, launcher.
