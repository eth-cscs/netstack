# slurm

> The workload manager. In the netstack it matters as a **launcher**: `srun`
> starts the ranks and provides the [PMI][cray-pmi] wire-up.

|  |  |
|---|---|
| Spack package | `slurm` |
| Layer | launch |
| Provided by | **system** |
| User-buildable | no (site-managed) |
| Slingshot component | — |
| Upstream | <https://slurm.schedmd.com/> |

## What it is

Slurm schedules jobs and, via `srun`, launches the processes of a parallel job.
For the netstack its relevant job is **process management**: `srun` places ranks
on nodes and speaks PMI/PMI-2 to bootstrap MPI, exchanging the information each
rank needs before the fabric can be used. It is one of the two launch paths on
Alps, the other being [cray-pals][cray-pals] under `mpiexec`.

Slurm itself does not move application data — that is the fabric
([libfabric][libfabric]/[XPMEM][xpmem]) — but a wire-up handled by the wrong or
mismatched PMI is a genuine netstack failure mode, which is why the launcher is
part of the picture.

## System vs. user

Always **system**: Slurm is installed and managed by the site. RPM `slurm`
(`25.5.4` on the reference node); `bin/system-stack` reports it.

## Identifying it

- `SLURM_*` environment variables in a job ⇒ launched under Slurm.
- `srun --mpi=list` shows the PMI plugins Slurm can provide.
- `bin/system-stack` reports the installed `slurm` version.

## Related

- [cray-pmi][cray-pmi] — the PMI libraries the launcher drives.
- [cray-pals][cray-pals] — the alternative (Cray) launcher.

[cray-pmi]: cray-pmi.md
[cray-pals]: cray-pals.md
[libfabric]: libfabric.md
[xpmem]: xpmem.md
