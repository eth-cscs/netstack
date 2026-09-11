[](){#ref-index}
# Netstack

Netstack is a set of tools for describing and diagnosing the network stack of applications on the [Alps](https://docs.cscs.ch/alps) system at CSCS.

The *netstack* of an application or environment is all the software that handles its inter-node and intra-node communication.
Together, these determine how an application communicates.

1. **drivers**, such as the CUDA driver and the Slingshot [CXI driver][ref-pkg-cxi-driver],
2. **libraries**, such as [libfabric][ref-pkg-libfabric], [libcxi][ref-pkg-libcxi], [MPI][ref-pkg-cray-mpich], [NCCL][ref-pkg-nccl] and [XPMEM][ref-pkg-xpmem], and
3. **environment variables**, such as `MPICH_GPU_SUPPORT_ENABLED`, `FI_MR_CACHE_MONITOR` and `NCCL_NET_PLUGIN`.


[](){#ref-index-system-user}
## System and user components

Every component comes from one of two halves of the stack.

[](){#ref-index-system}
### System components

The site pre-installs system components in the system image.

* All drivers are system components.
* HPE Cray EX systems also ship base libraries in the OS image, for example [libcxi][ref-pkg-libcxi], [libfabric][ref-pkg-libfabric] and [libxpmem][ref-pkg-xpmem].

The [`system-stack`][ref-tools-system-stack] tool reports the system components.

[](){#ref-index-user}
### User components

User components are software that is installed in user land, and can vary between user sessions.
Typically installed in a [uenv](https://docs.cscs.ch/software/uenv), a [container](https://docs.cscs.ch/software/container-engine), or a bare-metal Python or Spack environment.

Almost all environment variables are user components.
So are libraries such as [MPI][ref-pkg-cray-mpich], [NCCL][ref-pkg-nccl], [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] and the [CUDA toolkit][ref-pkg-cuda].

A few libraries, notably [libfabric][ref-pkg-libfabric] and [libcxi][ref-pkg-libcxi], can also exist in user land.
There, they replace the system copy.

The [`user-stack`][ref-tools-user-stack] tool reports user components.

[](){#ref-index-where-to-start}
## Where to start

| Section | Contents |
|---|---|
| [Tools][ref-tools]                        | The CLI tools for analysing and reporting netstacks. |
| [Analysing an environment][ref-analysis]  | The method to find what an environment contains. |
| [Environment variables][ref-envvars]      | The netstack-relevant variables, grouped by the component they affect. |
| [Packages][ref-pkg]                       | One reference page per component. |
| [Contributing][ref-contributing]          | How to build the documentation, and how to write it. |
