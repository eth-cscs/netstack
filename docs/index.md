[](){#ref-index}
# Netstack

Netstack is a set of tools and reference pages. The tools describe and diagnose the network stack of applications that run on the [Alps](https://www.cscs.ch/computers/alps) system at CSCS.

The *netstack* of an application or environment is all the software that handles its inter-node and intra-node communication:

1. **drivers**, such as the CUDA driver and the Slingshot [CXI driver][ref-pkg-cxi-driver],
2. **libraries**, such as [libfabric][ref-pkg-libfabric], [libcxi][ref-pkg-libcxi], [MPI][ref-pkg-cray-mpich], [NCCL][ref-pkg-nccl] and [XPMEM][ref-pkg-xpmem], and
3. **environment variables**, such as `MPICH_GPU_SUPPORT_ENABLED`, `FI_MR_CACHE_MONITOR` and `NCCL_NET_PLUGIN`.

Together, these determine how an application communicates.
A mismatch between any two of them can cause a crash or reduce performance. Such a mismatch is hard to see unless you list the whole set.

[](){#ref-index-system-user}
## System and user components

Every component comes from one of two halves of the stack.

[](){#ref-index-system}
### System components

The site pre-installs system components in the system image.
[`system-stack`][ref-tools-system-stack] reports them.

* All drivers are system components.
* HPE Cray EX systems also ship base libraries in the OS image, for example [libcxi][ref-pkg-libcxi], [libfabric][ref-pkg-libfabric] and [libxpmem][ref-pkg-xpmem].

[](){#ref-index-user}
### User components

Users install user components in user land: in a [uenv](https://eth-cscs.github.io/uenv/), a container, or an installation made with `pip`, `uv` or Spack.
[`user-stack`][ref-tools-user-stack] reports them.

Almost all environment variables are user components. So are libraries such as [MPI][ref-pkg-cray-mpich], [NCCL][ref-pkg-nccl], [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] and the [CUDA toolkit][ref-pkg-cuda].

A few libraries, notably [libfabric][ref-pkg-libfabric] and [libcxi][ref-pkg-libcxi], can also exist in user land. There, they replace the system copy.

[](){#ref-index-where-to-start}
## Where to start

| Section | Contents |
|---|---|
| [Tools][ref-tools]                        | The three tools in `bin/`, what each one reports, and where to run it. |
| [Analysing an environment][ref-analysis]  | The method to find what an environment contains. |
| [Environment variables][ref-envvars]      | The netstack-relevant variables, grouped by the component they affect. |
| [Packages][ref-pkg]                       | One reference page per component. |
| [Contributing][ref-contributing]          | How to build the documentation, and how to write it. |
