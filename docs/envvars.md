# Environment variables

Environment variables are **user components**: they are part of the netstack
just as much as the libraries, and are the most common lever for both tuning
and mis-configuration. This page is a reference of the netstack-relevant
variables, grouped by the component they affect.

`bin/user-stack` reports the variables from these families that are **currently
set** (prefixes `MPICH_`, `FI_`, `OFI_NCCL_`, `NCCL_`, `CXI_`, `PMI_`, `PALS_`,
`XPMEM`, `CUDA_`).

!!! tip "How to read the *Affects* column"
    A variable often crosses layers. `MPICH_GPU_SUPPORT_ENABLED` is read by
    [Cray MPICH][cray-mpich] but only does anything because [cray-gtl][cray-gtl]
    is present; `FI_MR_CACHE_MONITOR` is a [libfabric][libfabric] setting whose
    correct value depends on the [XPMEM][xpmem]/kernel combination underneath.

## Cray MPICH — `MPICH_*`

| Variable | Affects | Notes |
|---|---|---|
| `MPICH_GPU_SUPPORT_ENABLED` | [cray-mpich][cray-mpich], [cray-gtl][cray-gtl] | `1` enables GPU-aware MPI (pass GPU pointers to MPI). Requires the GTL library to be present. |
| `MPICH_GPU_IPC_ENABLED` | [cray-mpich][cray-mpich] | Intra-node GPU↔GPU transfers via CUDA IPC. |
| `MPICH_SMP_SINGLE_COPY_MODE` | [cray-mpich][cray-mpich], [xpmem][xpmem] | Intra-node single-copy transport: `XPMEM`, `CMA`, or `NONE`. |
| `MPICH_OFI_NIC_POLICY` | [cray-mpich][cray-mpich], [libfabric][libfabric] | How ranks are assigned to the multiple Slingshot NICs: `NUMA`, `BLOCK`, `ROUND-ROBIN`. |
| `MPICH_OFI_NIC_VERBOSE` | [cray-mpich][cray-mpich] | Print NIC-selection decisions (diagnostic). |
| `MPICH_ENV_DISPLAY` | [cray-mpich][cray-mpich] | Print every MPICH variable and its value at startup — invaluable for diagnosis. |
| `MPICH_VERSION_DISPLAY` | [cray-mpich][cray-mpich] | Print the MPICH/GTL version banner at startup. |
| `MPICH_MEMORY_REPORT` | [cray-mpich][cray-mpich] | Report high-water memory use per rank. |

## libfabric — `FI_*`

| Variable | Affects | Notes |
|---|---|---|
| `FI_PROVIDER` | [libfabric][libfabric] | Restrict the provider set (e.g. `cxi`). Normally left unset so the best provider is chosen. |
| `FI_MR_CACHE_MONITOR` | [libfabric][libfabric], [xpmem][xpmem] | Memory-registration cache monitor: `memhooks`, `userfaultfd`, `kdreg2`, or `disabled`. A frequent crash / corruption source when mismatched with the kernel — a prime **diagnostic** target. |
| `FI_HMEM` | [libfabric][libfabric], [cuda][cuda] | Enable heterogeneous (GPU) memory support in the provider. |
| `FI_LOG_LEVEL` / `FI_LOG_PROV` | [libfabric][libfabric] | Logging verbosity / restrict logging to a provider (e.g. `cxi`). |

### CXI provider — `FI_CXI_*`

The [CXI provider][libfabric] is the Slingshot-11 back-end inside libfabric.

| Variable | Affects | Notes |
|---|---|---|
| `FI_CXI_RX_MATCH_MODE` | [libfabric][libfabric], [libcxi][libcxi] | Tag-matching mode: `hardware`, `software`, `hybrid`. Falling back from hardware to software matching under pressure is a classic performance cliff. |
| `FI_CXI_RDZV_THRESHOLD` | [libfabric][libfabric] | Message size at which the rendezvous protocol takes over from eager. |
| `FI_CXI_RDZV_PROTO` | [libfabric][libfabric] | Rendezvous protocol variant (e.g. `default`, `alt_read`). |
| `FI_CXI_DEFAULT_CQ_SIZE` | [libfabric][libfabric] | Completion-queue depth; too small → `FI_EAGAIN` / retries at scale. |
| `FI_CXI_REQ_BUF_SIZE` / `FI_CXI_OFLOW_BUF_SIZE` | [libfabric][libfabric] | Unexpected-message and overflow buffer sizing. |
| `FI_CXI_OPTIMIZED_MRS` | [libfabric][libfabric], [libcxi][libcxi] | Use hardware-optimized memory regions. |
| `FI_CXI_DISABLE_HOST_REGISTER` | [libfabric][libfabric] | Skip registering host memory with the NIC (interacts with GDR). |

## aws-ofi-nccl — `OFI_NCCL_*`

| Variable | Affects | Notes |
|---|---|---|
| `OFI_NCCL_PROTOCOL` | [aws-ofi-nccl][aws-ofi-nccl] | Transport protocol used by the plugin (`RDMA`, `SENDRECV`). |
| `OFI_NCCL_GDR_FLUSH_DISABLE` | [aws-ofi-nccl][aws-ofi-nccl], [cuda][cuda] | Disable the GPUDirect RDMA flush; correctness-sensitive. |
| `OFI_NCCL_DISABLE_GDR_REQUIRED_CHECK` | [aws-ofi-nccl][aws-ofi-nccl] | Bypass the GDR-support sanity check. |
| `OFI_NCCL_NIC_DUP_CONNS` | [aws-ofi-nccl][aws-ofi-nccl] | Duplicate connections per NIC for bandwidth. |

## NCCL — `NCCL_*`

| Variable | Affects | Notes |
|---|---|---|
| `NCCL_NET_PLUGIN` | [nccl][nccl], [aws-ofi-nccl][aws-ofi-nccl] | Which network plugin NCCL loads (`ofi` → aws-ofi-nccl over libfabric/CXI). |
| `NCCL_NET` | [nccl][nccl] | Selected/observed transport, e.g. `AWS Libfabric`. |
| `NCCL_DEBUG` | [nccl][nccl] | Logging level: `WARN`, `INFO`, `TRACE`. `INFO` prints the chosen net plugin and topology. |
| `NCCL_DEBUG_SUBSYS` | [nccl][nccl] | Restrict debug output to subsystems (`NET`, `INIT`, `COLL`, …). |
| `NCCL_CROSS_NIC` | [nccl][nccl] | Allow rings/trees to cross NICs. |
| `NCCL_ALGO` / `NCCL_PROTO` | [nccl][nccl] | Force a collective algorithm / protocol (`Ring`, `Tree`; `LL`, `LL128`, `Simple`). |
| `NCCL_NVLS_ENABLE` | [nccl][nccl] | Enable NVLink SHARP (in-network reduction over NVLink). |

## Launcher / PMI — `PMI_*`, `PALS_*`

These are **populated by the launcher** ([Slurm][slurm] / [cray-pals][cray-pals]
via [cray-pmi][cray-pmi]) at job start — they describe rank/job identity and are
not normally set by hand. `user-stack` reports them because their presence
confirms the wire-up path.

| Variable | Affects | Notes |
|---|---|---|
| `PMI_RANK`, `PMI_SIZE`, `PMI_LOCAL_RANK`, `PMI_LOCAL_SIZE`, `PMI_UNIVERSE_SIZE` | [cray-pmi][cray-pmi] | Rank identity/topology for the PMI wire-up. |
| `PMI_CONTROL_PORT`, `PMI_SHARED_SECRET`, `PMI_JOBID` | [cray-pmi][cray-pmi] | Control-plane rendezvous for process management. |
| `PALS_*` (`PALS_RANKID`, `PALS_NODEID`, `PALS_APID`, …) | [cray-pals][cray-pals] | Set by the PALS launcher; per-rank/per-node identity. |

## CUDA — `CUDA_*`

| Variable | Affects | Notes |
|---|---|---|
| `CUDA_VISIBLE_DEVICES` | [cuda][cuda], [cuda-driver][cuda-driver] | Which GPUs the process sees; affects GPU↔NIC affinity. |
| `CUDA_HOME` | [cuda][cuda] | Toolkit root; set by the uenv view. |
| `CUDA_CACHE_PATH` | [cuda][cuda] | JIT compilation cache location. |
| `CUDA_MODULE_LOADING` | [cuda][cuda] | `EAGER`/`LAZY` module loading. |

[cray-mpich]: packages/cray-mpich.md
[cray-gtl]: packages/cray-gtl.md
[libfabric]: packages/libfabric.md
[libcxi]: packages/libcxi.md
[xpmem]: packages/xpmem.md
[nccl]: packages/nccl.md
[aws-ofi-nccl]: packages/aws-ofi-nccl.md
[cuda]: packages/cuda.md
[cuda-driver]: packages/cuda-driver.md
[cray-pmi]: packages/cray-pmi.md
[cray-pals]: packages/cray-pals.md
[slurm]: packages/slurm.md
