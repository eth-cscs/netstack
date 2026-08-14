# CSCS Netstack

Tools and reference documentation for describing and diagnosing the **network
stack** — the *netstack* — of applications running on the [Alps][alps] system
at CSCS.

A netstack is the full set of software involved in **inter-node** and
**intra-node** communication:

- **drivers** — e.g. the CUDA driver, the Slingshot [CXI][cxi-driver] driver;
- **libraries** — e.g. [libfabric][libfabric], [libcxi][libcxi],
  [MPI][cray-mpich], [NCCL][nccl], [XPMEM][xpmem];
- **environment variables** — e.g. `MPICH_GPU_SUPPORT_ENABLED`,
  `FI_MR_CACHE_MONITOR`, `NCCL_NET_PLUGIN` (see [Environment variables][envvars]).

Taken together these define exactly what an application runs with, and small
mismatches between them are a common source of crashes and lost performance.

## System vs. user components

Every component is provided by **one of two halves** of the stack. Knowing
which half a component comes from is the single most important fact when
reasoning about a netstack, because the two halves have different lifecycles
and different failure modes.

<div class="grid cards" markdown>

- :material-server: **System components**

    Pre-installed software provided by the system image.

    - Effectively all **drivers** (they must match the running kernel).
    - HPE Cray EX systems also ship base libraries — [libcxi][libcxi],
      [libfabric][libfabric], [libxpmem][xpmem] — in the OS image.
    - Detected with [`bin/system-stack`][tools].

- :material-account: **User components**

    Software brought in by the user, in a [uenv][uenv], a container, or a
    bare-metal install (`pip`/`uv`/Spack).

    - Effectively all **environment variables**.
    - Libraries such as [MPI][cray-mpich], [NCCL][nccl],
      [aws-ofi-nccl][aws-ofi-nccl], the [CUDA toolkit][cuda].
    - Some libraries ([libfabric][libfabric], [libcxi][libcxi]) can be shipped
      in user-land and **replace** the system copy.
    - Detected with [`bin/user-stack`][tools].

</div>

The same library name can therefore fall on either side depending on how the
environment is built. `prgenv-gnu/25.11` ships its own [libfabric][libfabric]
and [libcxi][libcxi] (user-provided); `prgenv-gnu/25.6` uses the host copies of
both. **Provenance is never guessed from a name** — it is established by
resolving the path the dynamic loader actually uses, and cross-checked against
the uenv's Spack database. See [Analysing a uenv][analysis].

## The components

Two flat lists, expanded per-package under [Packages][packages]:

### System components

| Component | Spack package | Role |
|---|---|---|
| [Slingshot CXI driver][cxi-driver]   | `cxi-driver`       | kernel driver for the Slingshot NIC |
| [Cassini headers][cassini-headers]   | `cassini-headers`  | hardware/ABI headers for Slingshot |
| [libcxi][libcxi]                     | `libcxi`           | user-space library over the CXI driver |
| [libfabric][libfabric]               | `libfabric`        | OFI fabric abstraction (base image copy) |
| [XPMEM][xpmem]                       | `xpmem`            | intra-node shared-memory kernel module |
| [CUDA driver][cuda-driver]           | `cuda-driver`      | userspace stub for the NVIDIA kernel driver |
| [Slurm][slurm]                       | `slurm`            | workload manager / launcher (PMI) |

### User components

| Component | Spack package | Role |
|---|---|---|
| [Cray MPICH][cray-mpich]     | `cray-mpich`    | MPI implementation (Slingshot-tuned) |
| [MPICH][mpich]               | `mpich`         | upstream MPI (ABI-compatible alternative) |
| [Open MPI][openmpi]          | `openmpi`       | alternative MPI implementation |
| [cray-gtl][cray-gtl]         | `cray-gtl`      | GPU transport layer for GPU-aware MPI |
| [libfabric][libfabric]       | `libfabric`     | OFI fabric abstraction (uenv copy) |
| [libcxi][libcxi]             | `libcxi`        | CXI user-space library (uenv copy) |
| [Cassini headers][cassini-headers] | `cassini-headers` | build-time headers for the CXI provider |
| [NCCL][nccl]                 | `nccl`          | GPU collective communication |
| [aws-ofi-nccl][aws-ofi-nccl] | `aws-ofi-nccl`  | routes NCCL over libfabric/CXI |
| [CUDA toolkit][cuda]         | `cuda`          | CUDA runtime + libraries |
| [XPMEM][xpmem]               | `xpmem`         | (can be user-provided) |
| [cray-pmi][cray-pmi]         | `cray-pmi`      | process management interface (Cray MPICH) |
| [PMIx][pmix]                 | `pmix`          | process management interface (Open MPI) |
| [cray-pals][cray-pals]       | `cray-pals`     | application launch service |

## The tools

| Tool | Reports | Run |
|---|---|---|
| [`bin/system-stack`][tools] | system half (RPM-based) | directly on a login/compute node |
| [`bin/user-stack`][tools]   | user half of a loaded uenv | inside `uenv run` |
| [`bin/spack-db`][tools]     | a uenv's Spack package database | inside `uenv run` (or `--mount`) |

See [Tools][tools] for usage, [Analysing a uenv][analysis] for the method, and
the [test-uenv skill](#) for how to drive a uenv non-interactively.

[alps]: https://www.cscs.ch/computers/alps
[uenv]: https://eth-cscs.github.io/uenv/
[tools]: tools.md
[analysis]: analysis/uenv.md
[packages]: packages/index.md
[envvars]: envvars.md
[libfabric]: packages/libfabric.md
[libcxi]: packages/libcxi.md
[cxi-driver]: packages/cxi-driver.md
[cassini-headers]: packages/cassini-headers.md
[cuda]: packages/cuda.md
[cuda-driver]: packages/cuda-driver.md
[cray-mpich]: packages/cray-mpich.md
[cray-gtl]: packages/cray-gtl.md
[mpich]: packages/mpich.md
[openmpi]: packages/openmpi.md
[nccl]: packages/nccl.md
[aws-ofi-nccl]: packages/aws-ofi-nccl.md
[xpmem]: packages/xpmem.md
[cray-pmi]: packages/cray-pmi.md
[pmix]: packages/pmix.md
[cray-pals]: packages/cray-pals.md
[slurm]: packages/slurm.md
