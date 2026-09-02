[](){#ref-envvars}
# Environment variables

Environment variables are [user components][ref-index-user].
They are as much a part of the netstack as the libraries are, and they are the most common lever for both tuning and misconfiguration.
This page lists the netstack-relevant variables, grouped by the component that reads them.

[`user-stack`][ref-tools-user-stack] reports the variables from these families that are currently set, by matching the prefixes `MPICH_`, `FI_`, `OFI_NCCL_`, `NCCL_`, `CXI_`, `PMI_`, `PALS_`, `XPMEM` and `CUDA_`.

!!! tip "How to read the component field"
    A variable often crosses layers.
    `MPICH_GPU_SUPPORT_ENABLED` is read by [Cray MPICH][ref-pkg-cray-mpich], but it only does anything when [cray-gtl][ref-pkg-cray-gtl] is present.
    `FI_MR_CACHE_MONITOR` is a [libfabric][ref-pkg-libfabric] setting whose correct value depends on the combination of [XPMEM][ref-pkg-xpmem] and kernel underneath it.
    In the JSON output each of these appears in `envvars` as `{"name": ..., "value": ..., "component": ...}`; see [JSON output][ref-json-output-user-stack].

[](){#ref-envvars-mpich}
## Cray MPICH

| Variable | Affects | Notes |
|---|---|---|
| `MPICH_GPU_SUPPORT_ENABLED` | [cray-mpich][ref-pkg-cray-mpich], [cray-gtl][ref-pkg-cray-gtl] | `1` enables GPU-aware MPI, so that GPU pointers can be passed to MPI. Requires the GTL library. |
| `MPICH_GPU_IPC_ENABLED` | [cray-mpich][ref-pkg-cray-mpich] | Intra-node GPU-to-GPU transfers through CUDA IPC. |
| `MPICH_SMP_SINGLE_COPY_MODE` | [cray-mpich][ref-pkg-cray-mpich], [xpmem][ref-pkg-xpmem] | Intra-node single-copy transport: `XPMEM`, `CMA` or `NONE`. |
| `MPICH_OFI_NIC_POLICY` | [cray-mpich][ref-pkg-cray-mpich], [libfabric][ref-pkg-libfabric] | How ranks are assigned to the Slingshot NICs: `NUMA`, `BLOCK` or `ROUND-ROBIN`. |
| `MPICH_OFI_NIC_VERBOSE` | [cray-mpich][ref-pkg-cray-mpich] | Print the NIC-selection decisions. |
| `MPICH_ENV_DISPLAY` | [cray-mpich][ref-pkg-cray-mpich] | Print every MPICH variable and its value at startup. |
| `MPICH_VERSION_DISPLAY` | [cray-mpich][ref-pkg-cray-mpich] | Print the MPICH and GTL version banner at startup. |
| `MPICH_MEMORY_REPORT` | [cray-mpich][ref-pkg-cray-mpich] | Report high-water memory use per rank. |

[](){#ref-envvars-openmpi}
## Open MPI

[Open MPI][ref-pkg-openmpi] is tuned through `OMPI_*` variables and MCA parameters rather than through `MPICH_*`.
The fabric-level `FI_*` variables below still apply, because Open MPI reaches Slingshot through the same [libfabric][ref-pkg-libfabric] `cxi` provider.

| Variable | Affects | Notes |
|---|---|---|
| `OMPI_MCA_pml` | [openmpi][ref-pkg-openmpi] | Point-to-point management layer, for example `cm` for the OFI MTL or `ob1` for the BTLs. |
| `OMPI_MCA_mtl`, `OMPI_MCA_btl` | [openmpi][ref-pkg-openmpi], [libfabric][ref-pkg-libfabric] | Select the transport. `ofi` routes traffic over libfabric and CXI. |
| `OMPI_MCA_opal_cuda_support` | [openmpi][ref-pkg-openmpi], [cuda][ref-pkg-cuda] | Force CUDA-aware support on or off. |

[](){#ref-envvars-libfabric}
## libfabric

| Variable | Affects | Notes |
|---|---|---|
| `FI_PROVIDER` | [libfabric][ref-pkg-libfabric] | Restrict the provider set, for example to `cxi`. Normally left unset, so that the best provider is chosen. |
| `FI_MR_CACHE_MONITOR` | [libfabric][ref-pkg-libfabric], [xpmem][ref-pkg-xpmem] | Memory-registration cache monitor: `memhooks`, `userfaultfd`, `kdreg2` or `disabled`. A frequent source of crashes and corruption when it is mismatched with the kernel, and so a common diagnostic target. |
| `FI_HMEM` | [libfabric][ref-pkg-libfabric], [cuda][ref-pkg-cuda] | Enable heterogeneous, that is GPU, memory support in the provider. |
| `FI_LOG_LEVEL`, `FI_LOG_PROV` | [libfabric][ref-pkg-libfabric] | Logging verbosity, and restriction of logging to one provider such as `cxi`. |

[](){#ref-envvars-cxi}
### CXI provider

The [CXI provider][ref-pkg-libfabric] is the Slingshot 11 back end inside libfabric.

| Variable | Affects | Notes |
|---|---|---|
| `FI_CXI_RX_MATCH_MODE` | [libfabric][ref-pkg-libfabric], [libcxi][ref-pkg-libcxi] | Tag-matching mode: `hardware`, `software` or `hybrid`. Falling back from hardware to software matching under pressure is a known performance cliff. |
| `FI_CXI_RDZV_THRESHOLD` | [libfabric][ref-pkg-libfabric] | Message size at which the rendezvous protocol takes over from eager. |
| `FI_CXI_RDZV_PROTO` | [libfabric][ref-pkg-libfabric] | Rendezvous protocol variant, for example `default` or `alt_read`. |
| `FI_CXI_DEFAULT_CQ_SIZE` | [libfabric][ref-pkg-libfabric] | Completion-queue depth. Too small a value causes `FI_EAGAIN` and retries at scale. |
| `FI_CXI_REQ_BUF_SIZE`, `FI_CXI_OFLOW_BUF_SIZE` | [libfabric][ref-pkg-libfabric] | Sizing of the unexpected-message and overflow buffers. |
| `FI_CXI_OPTIMIZED_MRS` | [libfabric][ref-pkg-libfabric], [libcxi][ref-pkg-libcxi] | Use hardware-optimized memory regions. |
| `FI_CXI_DISABLE_HOST_REGISTER` | [libfabric][ref-pkg-libfabric] | Skip registering host memory with the NIC. Interacts with GPUDirect RDMA. |

[](){#ref-envvars-aws-ofi-nccl}
## aws-ofi-nccl

| Variable | Affects | Notes |
|---|---|---|
| `OFI_NCCL_PROTOCOL` | [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] | Transport protocol used by the plugin: `RDMA` or `SENDRECV`. |
| `OFI_NCCL_GDR_FLUSH_DISABLE` | [aws-ofi-nccl][ref-pkg-aws-ofi-nccl], [cuda][ref-pkg-cuda] | Disable the GPUDirect RDMA flush. Correctness-sensitive. |
| `OFI_NCCL_DISABLE_GDR_REQUIRED_CHECK` | [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] | Bypass the GPUDirect RDMA support check. |
| `OFI_NCCL_NIC_DUP_CONNS` | [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] | Number of duplicate connections per NIC, used to raise bandwidth. |

[](){#ref-envvars-nccl}
## NCCL

| Variable | Affects | Notes |
|---|---|---|
| `NCCL_NET_PLUGIN` | [nccl][ref-pkg-nccl], [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] | Which network plugin NCCL loads. `ofi` selects aws-ofi-nccl over libfabric and CXI. |
| `NCCL_NET` | [nccl][ref-pkg-nccl] | The selected transport, reported as for example `AWS Libfabric`. |
| `NCCL_DEBUG` | [nccl][ref-pkg-nccl] | Logging level: `WARN`, `INFO` or `TRACE`. `INFO` prints the chosen net plugin and the topology. |
| `NCCL_DEBUG_SUBSYS` | [nccl][ref-pkg-nccl] | Restrict debug output to subsystems such as `NET`, `INIT` or `COLL`. |
| `NCCL_CROSS_NIC` | [nccl][ref-pkg-nccl] | Allow rings and trees to cross NICs. |
| `NCCL_ALGO`, `NCCL_PROTO` | [nccl][ref-pkg-nccl] | Force a collective algorithm, `Ring` or `Tree`, or a protocol, `LL`, `LL128` or `Simple`. |
| `NCCL_NVLS_ENABLE` | [nccl][ref-pkg-nccl] | Enable NVLink SHARP, which reduces in the network over NVLink. |

[](){#ref-envvars-launcher}
## Launcher and PMI

These variables are populated by the launcher, either [Slurm][ref-pkg-slurm] or [cray-pals][ref-pkg-cray-pals] through [cray-pmi][ref-pkg-cray-pmi], when the job starts.
They describe rank and job identity, and are not normally set by hand.
`user-stack` reports them because their presence confirms which wire-up path is in use.

| Variable | Affects | Notes |
|---|---|---|
| `PMI_RANK`, `PMI_SIZE`, `PMI_LOCAL_RANK`, `PMI_LOCAL_SIZE`, `PMI_UNIVERSE_SIZE` | [cray-pmi][ref-pkg-cray-pmi] | Rank identity and topology for the PMI wire-up. |
| `PMI_CONTROL_PORT`, `PMI_SHARED_SECRET`, `PMI_JOBID` | [cray-pmi][ref-pkg-cray-pmi] | Control-plane rendezvous for process management. |
| `PMIX_RANK`, `PMIX_NAMESPACE`, `PMIX_SERVER_URI*` and the rest of `PMIX_*` | [pmix][ref-pkg-pmix] | The PMIx equivalent, used by [Open MPI][ref-pkg-openmpi] and set by the PMIx server of the launcher. |
| `PALS_RANKID`, `PALS_NODEID`, `PALS_APID` and the rest of `PALS_*` | [cray-pals][ref-pkg-cray-pals] | Per-rank and per-node identity, set by the PALS launcher. |

[](){#ref-envvars-cuda}
## CUDA

| Variable | Affects | Notes |
|---|---|---|
| `CUDA_VISIBLE_DEVICES` | [cuda][ref-pkg-cuda], [cuda-driver][ref-pkg-cuda-driver] | Which GPUs the process sees, which in turn affects GPU-to-NIC affinity. |
| `CUDA_HOME` | [cuda][ref-pkg-cuda] | Toolkit root, set by the uenv view. |
| `CUDA_CACHE_PATH` | [cuda][ref-pkg-cuda] | Location of the JIT compilation cache. |
| `CUDA_MODULE_LOADING` | [cuda][ref-pkg-cuda] | Module loading mode, `EAGER` or `LAZY`. |
