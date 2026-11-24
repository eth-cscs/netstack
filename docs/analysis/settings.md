[](){#ref-analysis-settings}
# Measured effect of settings

This page records measurements of [environment variables][ref-envvars] and launch options on Alps.
Each section states what was measured, on which nodes, and what the numbers do not cover.

Use the numbers to compare settings with each other.
Do not use them as reference values for another cluster, node type or library version.

[](){#ref-analysis-settings-environment}
## Test environment

All measurements on this page come from the same environment, unless a section states a difference.

| Property | Value |
|---|---|
| Cluster | Daint, `normal` partition |
| Node type | Grace-Hopper, 4 GPUs and 4 Slingshot NICs on each node |
| Environment | The `torch` view of the `pytorch/v2.14.1` uenv |
| libfabric | 2.6.0 |
| Cray MPICH | 9.1.0 |
| NCCL | 2.30.7 |
| aws-ofi-nccl | 1.20.0 |
| Date | November 2026 |

The MPI numbers come from the OSU micro-benchmarks 7.5.2 in the uenv, with one rank on each node.
The NCCL numbers come from `all_reduce_perf` and `sendrecv_perf` of nccl-tests, with one rank for each GPU.

[](){#ref-analysis-settings-rdzv}
## Eager and rendezvous messages

The CXI provider of [libfabric][ref-pkg-libfabric] sends a small message with the eager protocol: the data travels with the message header.
It sends a large message with the rendezvous protocol: the receiver fetches the data after it matched the header.
`FI_CXI_RDZV_THRESHOLD`, `FI_CXI_RDZV_GET_MIN` and `FI_CXI_RDZV_EAGER_SIZE` control where one protocol takes over from the other.

The Alps extended images, the Container Engine hook and the `pytorch` views set all three to `0`.
The CSCS documentation gives the same values as a workaround for NCCL hangs and watchdog timeouts.

### Which variables have an effect

The table gives the latency of `osu_latency` at 256 bytes between two nodes of one group, with host buffers.
Each row starts from the `torch` view, which sets all three variables to `0`.

| Setting | Latency (us) |
|---|---|
| All three variables are `0` | 10.8 to 10.9 |
| `FI_CXI_RDZV_EAGER_SIZE` is unset | 11.4 |
| `FI_CXI_RDZV_GET_MIN` is unset | 3.1 to 3.2 |
| `FI_CXI_RDZV_THRESHOLD` is unset | 3.1 to 3.2 |
| All three variables are unset | 3.1 |

The eager protocol is off only when `FI_CXI_RDZV_THRESHOLD` and `FI_CXI_RDZV_GET_MIN` are both `0`.
One variable with the value `0` has no effect at this message size, and `FI_CXI_RDZV_EAGER_SIZE` has no effect at all at this message size.
On nine node pairs, each variable set to `0` alone gave the same latency and bandwidth as no variable set.

Messages of 8 to 128 bytes are not affected: the latency is 1.9 us at 8 bytes with every setting.

### Effect on MPI

The table compares all three variables at `0` with all three unset, on seven node pairs that are each in one group.

| Benchmark at 256 bytes | All `0` | Unset |
|---|---|---|
| `osu_latency`, host buffers (us) | 8.9 to 10.9 | 2.7 to 3.2 |
| `osu_latency`, GPU buffers (us) | 9.6 to 11.6 | 3.5 to 3.9 |
| `osu_bw`, host buffers (MB/s) | 268 to 303 | 527 to 625 |
| `osu_bw`, GPU buffers (MB/s) | 226 to 251 | 384 to 457 |

On 4 nodes, the latency is higher from 256 bytes to 16 KiB, and `osu_bw` with GPU buffers is 2.3 times lower from 4 KiB to 16 KiB.
From 32 KiB there is no difference, and the results at 4 MiB are the same.

The rendezvous latency also depends on two other settings of the view.
With all three variables at `0`, the latency at 256 bytes is 10.9 us with the view, 7.4 us without `FI_CXI_RDZV_PROTO=alt_read`, and 5.6 us without `SLURM_NETWORK=disable_rdzv_get`.

### Effect on NCCL

The table compares the same two settings for an NCCL all-reduce on 4 nodes with 16 GPUs.

| Message size | All `0` | Unset |
|---|---|---|
| 16 KiB (GB/s) | 0.55 | 0.88 |
| 16 MiB (GB/s) | 25.6 | 21.6 |
| 64 MiB (GB/s) | 86 | 76 |
| 256 MiB and more | same | same |

Up to 64 KiB the all-reduce is 37% slower with the variables at `0`.
From 256 KiB to 64 MiB it is 13% to 18% faster, for example 15% at 1 MiB.
NCCL send-receive from 64 KiB, and a `torch.distributed` all-reduce of 1 GiB, are the same with both settings.

With only `FI_CXI_RDZV_EAGER_SIZE=0`, small messages are as fast as with no variable set, and the gain at 64 MiB remains. The gain at 16 MiB does not remain.

!!! warning "These benchmarks do not test the reason for the settings"
    The settings are a workaround for hangs and timeouts of NCCL applications.
    A benchmark of bandwidth and latency does not reproduce those failures.
    Do not remove the settings from an environment for NCCL applications because of the numbers on this page.

### Consequence for tests

A test that compares the latency of a 256 byte message with a reference fails in an environment with these settings, although the MPI library and the network are healthy.
Check the value of `FI_CXI_RDZV_THRESHOLD` and `FI_CXI_RDZV_GET_MIN` in the job before you read such a result.

[](){#ref-analysis-settings-disable-rdzv-get}
## The `disable_rdzv_get` network option

`disable_rdzv_get` is a value of the `srun` option `--network`, which configures the Slingshot NIC for the job.
`SLURM_NETWORK=disable_rdzv_get` in the environment of `srun` has the same effect.
`FI_CXI_RDZV_PROTO=alt_read` needs the option.

The table gives the bus bandwidth of an NCCL all-reduce of 4 GiB on 4 nodes with 16 GPUs, in GB/s.

| Environment | Without the option | With the option |
|---|---|---|
| Alps extended image, 26.07 | 74 | 93 |
| uenv with the settings of the image | 74 | 93 |
| uenv with the default rendezvous settings of libfabric | 74 | 91 |

The option is what matters. The `alt_read` protocol adds 2 GB/s when the option is set.

On 2 nodes the all-reduce is 126 to 128 GB/s without the option and 129 to 131 GB/s with it.
A `torch.distributed` all-reduce of 1 GiB on 16 ranks is 75 GB/s without the option and 92 GB/s with it.
The option has no clear effect on Cray MPICH: `osu_bw` and `osu_allreduce` are the same within the noise of single runs.

[](){#ref-analysis-settings-cross-nic}
## NCCL NIC selection

`NCCL_CROSS_NIC=0` and `NCCL_PXN_DISABLE=1` are the values of the Alps extended images and of the Container Engine hook.
`NCCL_CROSS_NIC=1` without `NCCL_PXN_DISABLE` is the value of the NCCL guide and of the `pytorch/v2.9.1` view.

The table gives NCCL bandwidth on 2 nodes with 8 GPUs, in GB/s.

| Collective and message size | `0` and `1` | `1` and unset |
|---|---|---|
| All-reduce, 1 MiB | 6.7 | 15.7 |
| All-gather, 1 MiB | 5.0 | 11.5 |
| All-reduce, 64 MiB | 108 | 114 |
| All-reduce, 1 GiB | 154 | 149 |

The values of the extended images halve the bandwidth of mid-size collectives on 2 nodes, and are 3% faster at 1 GiB.
The measurement covers 2 and 4 nodes only.
It does not show which values are better for a large job, which is the case that the extended images tune for.

[](){#ref-analysis-settings-other}
## Settings with no measured effect

These settings of the extended images made no measurable difference in OSU point-to-point benchmarks and NCCL collectives up to 4 GiB on 1, 2 and 4 nodes:

* `FI_CXI_SAFE_DEVMEM_COPY_THRESHOLD=16777216`,
* `FI_MR_CACHE_MAX_SIZE=-1`, and
* `FI_MR_CACHE_MAX_COUNT=524288`.

`FI_CXI_RX_MATCH_MODE` and `FI_CXI_RDZV_PROTO` made no difference to `osu_latency` up to 1 KiB when the eager protocol is on.

[](){#ref-analysis-settings-placement}
## Node placement

The latency between two nodes depends on where Slurm places them.
This is not a setting of the netstack, but it changes every latency measurement on this page.

Slurm on Daint describes the network as a tree with one level. Each entry that `scontrol show topology` prints is one dragonfly group of about 110 nodes, named `group16` to `group27`.
A Slurm "switch" is therefore a group, not a physical switch.

The table gives the latency of `osu_latency` with host buffers, with the eager protocol on, for twelve jobs of two nodes.

| Placement of the two nodes | Jobs | 8 bytes (us) | 256 bytes (us) |
|---|---|---|---|
| Same group, lower latency | 3 | 1.9 | 2.7 |
| Same group, higher latency | 8 | 2.2 | 3.0 |
| Different groups | 1 | 3.35 | 4.2 |

`sbatch --switches=1` keeps the nodes of a job in one group.
Six jobs with the option all ran in one group. One of six jobs without the option ran in two groups.
The option does not select between the two levels inside a group, and the node names do not predict the level.

Use `--switches=1` for a latency test on two nodes, or record the group of each node with the result.
