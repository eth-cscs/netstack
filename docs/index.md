[](){#ref-index}
# Netstack

Netstack is a set of tools and reference pages for describing and diagnosing the network stack of applications that run on the [Alps](https://www.cscs.ch/computers/alps) system at CSCS.

The *netstack* of an application or environment is all of the software involved in its inter-node and intra-node communication:

1. **drivers**, such as the CUDA driver and the Slingshot [CXI driver][ref-pkg-cxi-driver],
2. **libraries**, such as [libfabric][ref-pkg-libfabric], [libcxi][ref-pkg-libcxi], [MPI][ref-pkg-cray-mpich], [NCCL][ref-pkg-nccl] and [XPMEM][ref-pkg-xpmem], and
3. **environment variables**, such as `MPICH_GPU_SUPPORT_ENABLED`, `FI_MR_CACHE_MONITOR` and `NCCL_NET_PLUGIN`.

Together these determine how an application performs communication.
A mismatch between any two of them can cause a crash or cost performance, and such a mismatch is hard to see without listing the whole set.

[](){#ref-index-system-user}
## System and user components

Every component comes from one of two halves of the stack.

[](){#ref-index-system}
### System components

System components are pre-installed by the site, in the system image.
They are reported by [`system-stack`][ref-tools-system-stack].

* all drivers are system components.
* HPE Cray EX systems also ship base libraries in the OS image, for example [libcxi][ref-pkg-libcxi], [libfabric][ref-pkg-libfabric] and [libxpmem][ref-pkg-xpmem].

[](){#ref-index-user}
### User components

User components are installed in user land: in a [uenv](https://eth-cscs.github.io/uenv/), a container, or an installation made with `pip`, `uv` or Spack.
They are reported by [`user-stack`][ref-tools-user-stack].

Effectively all environment variables are user components, as are libraries such as [MPI][ref-pkg-cray-mpich], [NCCL][ref-pkg-nccl], [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] and the [CUDA toolkit][ref-pkg-cuda].

A few libraries, notably [libfabric][ref-pkg-libfabric] and [libcxi][ref-pkg-libcxi], can be shipped in user land, where they replace the system copy.

[](){#ref-index-where-to-start}
## Where to start

| Section | Contents |
|---|---|
| [Tools][ref-tools]                        | The three tools in `bin/`, what each one reports, and where to run it. |
| [Analysing an environment][ref-analysis]  | The method used to establish what an environment contains. |
| [Environment variables][ref-envvars]      | The netstack-relevant variables, grouped by the component they affect. |
| [Packages][ref-pkg]                       | One reference page per component. |
| [Contributing][ref-contributing]          | How to build the documentation, and how to write it. |
