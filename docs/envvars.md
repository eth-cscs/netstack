[](){#ref-envvars}
# Environment variables

Environment variables are [user components][ref-index-user].
They are the most common way to tune the netstack, and the most common source of misconfiguration.

This page lists the variables that CSCS sets, recommends or has measured on Alps.
It is not a reference for every variable that a library reads.
The upstream documentation of each library is that reference.

[`user-stack`][ref-tools-user-stack] reports the variables that are currently set. It matches the prefixes `MPICH_`, `FI_`, `OFI_NCCL_`, `NCCL_`, `CXI_`, `PMI_`, `PALS_`, `XPMEM` and `CUDA_`.
In the JSON output, each variable appears in `envvars` as `{"name": ..., "value": ..., "component": ...}`. See [JSON output][ref-json-output-user-stack] for details.

[](){#ref-envvars-inclusion}
## What this page lists

A variable is on this page only if one of the following is true:

1. a [source][ref-envvars-sources] at CSCS sets it or recommends it, or
2. CSCS measured its effect on Alps, and [Measured effect of settings][ref-analysis-settings] records the measurement.

Each entry names the source and the value.
A variable that is known only from a manual page does not belong here.

!!! warning "The sources do not agree on every value"
    The sources were written at different times and for different workloads.
    The tables below show the value in each source side by side, so that a difference is visible.
    A difference is not always an error. See the notes under each table.

[](){#ref-envvars-sources}
## Where the settings come from

| Source | What it is | Applies to |
|---|---|---|
| NCCL guide | The recommended variables in the [NCCL page](https://docs.cscs.ch/software/communication/nccl/) of the CSCS documentation. | Users who set variables by hand. |
| Extended images | The runtime defaults of the [Alps extended images](https://github.com/eth-cscs/alps-extended-images), in `Alps-Images/common/` and `Alps-Images/NGC/`. | Containers built from these images. |
| CE hook | The defaults that the Container Engine sets when the `aws_ofi_nccl` hook is enabled. They have the same values as the extended images. | Containers that enable the hook. |
| uenv view | The `env_vars` section of a recipe in [alps-uenv](https://github.com/eth-cscs/alps-uenv). | Jobs that load the view. |
| ReFrame test | The variables that a test in [cscs-reframe-tests](https://github.com/eth-cscs/cscs-reframe-tests) exports in its job script. | The test only. |

A variable that a test exports replaces the value from a view or a container.
Read the job script before you compare a test result with a result from the same environment outside the test.

The `torch` view of `pytorch/v2.14.1` follows the extended images.
Its values are the values in the *Extended images* column, and it adds `NCCL_GRAPH_REGISTER` and `SLURM_NETWORK`.

[](){#ref-envvars-libfabric}
## libfabric

All of these variables belong to [libfabric][ref-pkg-libfabric].
The `FI_CXI_*` variables belong to its CXI provider.
A dash means that the source does not set the variable.

| Variable | NCCL guide | Extended images, CE hook | `pytorch/v2.9.1` view | ReFrame NCCL test |
|---|---|---|---|---|
| `FI_PROVIDER` | - | `cxi` | `cxi` | - |
| `FI_CXI_DEFAULT_CQ_SIZE` | `131072` | `131072` | `131072` | `131072` |
| `FI_CXI_DEFAULT_TX_SIZE` | `16384` | `16384` | `16384` | `32768` |
| `FI_CXI_DISABLE_HOST_REGISTER` | `1` | `1` | `1` | `1` |
| `FI_CXI_RX_MATCH_MODE` | `software` | `hybrid` | `hybrid` | `software` |
| `FI_MR_CACHE_MONITOR` | `userfaultfd` | `userfaultfd` | `userfaultfd` | `userfaultfd` |
| `FI_MR_CACHE_MAX_SIZE` | - | `-1` | - | - |
| `FI_MR_CACHE_MAX_COUNT` | - | `524288` | - | - |
| `FI_CXI_RDZV_THRESHOLD` | `0`, as a workaround | `0` | `0` | `0` |
| `FI_CXI_RDZV_GET_MIN` | `0`, as a workaround | `0` | `0` | `0` |
| `FI_CXI_RDZV_EAGER_SIZE` | `0`, as a workaround | `0` | `0` | `0` |
| `FI_CXI_RDZV_PROTO` | - | `alt_read` | `alt_read` | - |
| `FI_CXI_SAFE_DEVMEM_COPY_THRESHOLD` | - | `16777216` | - | - |

`FI_CXI_RDZV_THRESHOLD`, `FI_CXI_RDZV_GET_MIN` and `FI_CXI_RDZV_EAGER_SIZE`
:   The NCCL guide gives the three variables as a workaround for NCCL hangs and watchdog timeouts.
    The extended images set them for every job.
    They turn off the eager protocol for messages of 256 bytes and more, which makes small MPI messages slower.
    Only `FI_CXI_RDZV_THRESHOLD` and `FI_CXI_RDZV_GET_MIN` together have this effect.
    See [eager and rendezvous messages][ref-analysis-settings-rdzv].

`FI_CXI_RDZV_PROTO`
:   The value `alt_read` needs the Slurm network option `disable_rdzv_get`. See [Slurm][ref-envvars-slurm].

`FI_CXI_RX_MATCH_MODE`
:   The sources use `software` and `hybrid`.
    The value made no difference to the latency of small MPI messages in the [measurements][ref-analysis-settings-rdzv].

`FI_MR_CACHE_MONITOR`
:   Every source sets `userfaultfd`.
    The Cray MPICH page of the CSCS documentation gives `disabled` as a workaround for hangs, and states that `userfaultfd` can also avoid them and is faster.

`FI_CXI_SAFE_DEVMEM_COPY_THRESHOLD`
:   The Cray MPICH page of the CSCS documentation gives the value `0` as a workaround for the `cxil_map: write error` message with GPU-aware MPI. The value `0` turns off gdrcopy, and makes small messages slower.
    The value `16777216` of the extended images made no measurable difference in the [communication benchmarks][ref-analysis-settings-other].

`FI_CXI_DEFAULT_TX_SIZE`
:   The ReFrame NCCL test and the ReFrame Megatron-LM test use `32768`. Every other source uses `16384`.

[](){#ref-envvars-nccl}
## NCCL

[NCCL][ref-pkg-nccl] reads these variables.
`NCCL_NET` selects the [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] plugin.
No source at CSCS sets a variable of the `OFI_NCCL_*` family.

| Variable | NCCL guide | Extended images, CE hook | `pytorch/v2.9.1` view | ReFrame NCCL test |
|---|---|---|---|---|
| `NCCL_NET` | `AWS Libfabric` | `AWS Libfabric` | `AWS Libfabric` | `AWS Libfabric` |
| `NCCL_NET_GDR_LEVEL` | `PHB` | `PHB` | `PHB` | `PHB` |
| `NCCL_PROTO` | `^LL128` | `^LL128` | `^LL128` | `^LL128` |
| `NCCL_CROSS_NIC` | `1` | `0` | `1` | `0` |
| `NCCL_PXN_DISABLE` | - | `1` | - | `1` |
| `NCCL_NCHANNELS_PER_NET_PEER` | `4`, optional | `4` | `4` | `4`, send-receive only |
| `NCCL_P2P_LEVEL` | - | `NVL` | `NVL` | - |
| `NCCL_NET_GDR_C2C` | - | `1` | `1` | - |
| `NCCL_NET_GDR_READ` | - | `1` | `1` | - |
| `NCCL_SOCKET_IFNAME` | - | `hsn` | - | - |
| `NCCL_SOCKET_NTHREADS` | - | `4` | - | - |
| `NCCL_NSOCKS_PERTHREAD` | - | `1` | - | - |
| `NCCL_DEBUG` | `WARN`, to diagnose | - | - | `Info` |

`NCCL_NET`
:   With the value `AWS Libfabric`, an application fails at startup if NCCL cannot find the plugin.
    Without it, NCCL falls back to TCP sockets and the application runs slowly.

`NCCL_CROSS_NIC` and `NCCL_PXN_DISABLE`
:   The sources disagree.
    The Container Engine changed `NCCL_CROSS_NIC` from `1` to `0` and added `NCCL_PXN_DISABLE=1` when it took over the values of the extended images.
    On 2 nodes, the values `0` and `1` of the extended images halve the bandwidth of NCCL collectives at 1 MiB.
    See [NCCL NIC selection][ref-analysis-settings-cross-nic].

`NCCL_PROTO`
:   NCCL 2.27 enabled the `LL128` protocol by default. The value `^LL128` turns it off, because it is slower on Slingshot.

`NCCL_NET_PLUGIN`
:   The extended images unset this variable.
    The NGC PyTorch image sets it to a plugin that does not exist on Alps, and NCCL then ignores `NCCL_NET`.

`NCCL_GRAPH_REGISTER`
:   The `torch` view of `pytorch/v2.14.1` sets `0`.
    With the default, an inter-node collective inside a CUDA graph fails with `unhandled cuda error` in `ncclGroupEnd`.

`NCCL_DEBUG`
:   With `INFO`, NCCL prints the network plugin that it selected. The ReFrame NCCL test checks this output for the `cxi` provider.

[](){#ref-envvars-slurm}
## Slurm

| Variable | Value | Source |
|---|---|---|
| `SLURM_NETWORK` | `disable_rdzv_get` | The `torch` view of `pytorch/v2.14.1`, and the test scripts of the extended images. |

`SLURM_NETWORK` is the environment form of the `srun` option `--network`.
The CSCS documentation of the extended images requires `--network=disable_rdzv_get` for NCCL jobs.
On 4 nodes, an NCCL all-reduce reaches 93 GB/s with the option and 74 GB/s without it.
See [the `disable_rdzv_get` network option][ref-analysis-settings-disable-rdzv-get].

!!! warning "A view cannot set the option for the `srun` that loads it"
    `srun` reads `SLURM_NETWORK` when it starts.
    A job script with `#SBATCH --uenv` and `#SBATCH --view` has the variable in its environment, and every `srun` in the script uses it.
    A direct `srun --uenv=... --view=...` starts before the view is applied, and does not use it. Pass `--network=disable_rdzv_get` to that `srun`.

[](){#ref-envvars-mpich}
## Cray MPICH and MPICH

| Variable | Value | Source |
|---|---|---|
| `MPICH_GPU_SUPPORT_ENABLED` | `1` | CSCS documentation, for GPU-aware MPI. Some clusters and views set it by default. |
| `MPICH_GPU_SUPPORT_ENABLED` | `0` | CSCS documentation, for applications that use NCCL, or that only send host buffers. |
| `MPIR_CVAR_NO_LOCAL` | `1` | CSCS documentation, as a workaround for slow intra-node host communication. |
| `MPIR_CVAR_CH4_OFI_ENABLE_HMEM` | `1` | CSCS documentation, for GPU-aware communication with [MPICH][ref-pkg-mpich]. |

`MPICH_GPU_SUPPORT_ENABLED`
:   [Cray MPICH][ref-pkg-cray-mpich] reads the variable, and the value `1` needs the [cray-gtl][ref-pkg-cray-gtl] library.
    An application that sends a GPU buffer without it fails with a segmentation fault.
    The `torch` view of `pytorch/v2.14.1` sets `1`. The CSCS documentation recommends `0` when NCCL and GPU-aware MPI can run at the same time, because the combination can deadlock.

[](){#ref-envvars-openmpi}
## Open MPI

[Open MPI][ref-pkg-openmpi] reaches Slingshot through the [libfabric][ref-pkg-libfabric] `cxi` provider, so the `FI_*` variables above apply.
The CSCS documentation and the extended images set the same values.

| Variable | Value | Reason |
|---|---|---|
| `PMIX_MCA_psec` | `native` | [PMIx][ref-pkg-pmix] uses the security domain of Slurm. Without it, PMIx prints warnings at startup. |
| `FI_PROVIDER` | `cxi` | Open MPI uses the CXI provider. |
| `OMPI_MCA_pml` | `cm` | Open MPI uses the `cm` component for point-to-point communication. |
| `OMPI_MCA_mtl` | `ofi` | Open MPI sends through libfabric. |
| `OMPI_MCA_btl` | `^tcp,uct,usnic` | Extended images only. Open MPI does not use these transports. |

The CSCS documentation of Open MPI also describes a second configuration, which uses the LINKx provider with `FI_PROVIDER=lnx`, `FI_LNX_PROV_LINKS`, `FI_SHM_USE_XPMEM=1` and `OMPI_MCA_mtl_ofi_av=table`.

[](){#ref-envvars-launcher}
## Launcher and PMI

The launcher sets the `PMI_*`, `PMIX_*` and `PALS_*` variables when a job starts. The launcher is [Slurm][ref-pkg-slurm] or [cray-pals][ref-pkg-cray-pals].
The variables carry the identity of each rank, and users do not set them.
`user-stack` reports them because they show which wire-up path the job uses: [cray-pmi][ref-pkg-cray-pmi], [PMIx][ref-pkg-pmix] or PALS.

[](){#ref-envvars-cuda}
## CUDA

| Variable | Value | Source |
|---|---|---|
| `CUDA_HOME` | The path of the view | uenv views. |
| `CUDA_CACHE_DISABLE` | `1` | Extended images, CE hook and the `pytorch` views. |
| `CUDA_VISIBLE_DEVICES` | `0` | The ReFrame OSU tests with GPU buffers, which use one GPU on each node. |

`CUDA_CACHE_DISABLE`
:   The value `1` turns off the cache of JIT-compiled kernels.
    Ranks that share one cache directory can corrupt it.

[](){#ref-envvars-contributing}
## Adding a variable

Add a variable to this page when a source sets it, or when you measured it on Alps.

1. For a setting, add a row to the table of its component, with the value in each source. Add a source to [the list of sources][ref-envvars-sources] if it is new.
2. For a measurement, add the method and the numbers to [Measured effect of settings][ref-analysis-settings], and link to them from a note under the table.
3. State what the measurement covers: the cluster, the node type, the number of nodes and the versions of the libraries.

Do not copy the description of a variable from the manual page of the library. Link to the manual page.
