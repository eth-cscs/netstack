[](){#ref-pkg-cray-mpich}
# cray-mpich

Cray MPICH is HPE's MPI implementation, tuned for the Slingshot fabric. It is the default MPI on Alps.

| Property | Value |
|---|---|
| Spack package | `cray-mpich` |
| Layer | MPI |
| Provided by | User, through a uenv or a module. |
| User-buildable | No, it is a binary redistributed by HPE. |
| Slingshot component | Indirectly, through [libfabric][ref-pkg-libfabric]. |
| Upstream | <https://docs.nersc.gov/development/compilers/wrappers/> |

## What it is

HPE derives Cray MPICH from [MPICH][ref-pkg-mpich] and tunes it for Slingshot.
It is ABI-compatible with MPICH `3.4a2`, and it uses the `ch4:ofi` device. An application built against upstream MPICH therefore runs against it unchanged.
It reaches the network through [libfabric][ref-pkg-libfabric] and the CXI provider. For GPU-aware transfers, it goes through [cray-gtl][ref-pkg-cray-gtl].

The compiler wrappers `mpicc`, `mpicxx` and `mpifort` on the view `PATH` wrap the GCC in the uenv.

```console title="Inspecting a Cray MPICH build"
$ mpicc -show
gcc ... -lmpi_gnu_123 -lmpi_gtl_cuda ...
$ mpichversion
```

`mpicc -show` shows the link line, and `mpichversion` prints the full build configuration.

### Runtime dependencies

The dependency tree of the MPI library has this shape:

```text title="Dependencies of libmpi_gnu_123"
libmpi_gnu_123 → libmpi_gtl_cuda   (GPU-aware transfers, cray-gtl)
               → libfabric.so.1    → libcxi.so.1 → Slingshot NIC
               → libpmi, libpmi2   (cray-pmi, launch and wire-up)
               → libxpmem          (intra-node shared memory)
               → libcudart, libcuda
```

## System or user

Cray MPICH is a user component.
It comes from the uenv, or from a `cray-mpich` module, and it appears directly on the view path.

For some dependencies, in particular [libfabric][ref-pkg-libfabric] and [libcxi][ref-pkg-libcxi], the system provides one component and the user provides another.
Their own pages cover them.

## Identifying it

[`user-stack`][ref-tools-user-stack] reports the `cray-mpich` package version together with the MPICH version it is ABI-compatible with.

| Environment | cray-mpich version | MPICH base |
|---|---|---|
| `prgenv-gnu/25.11:v1` | 8.1.32 | 3.4a2 |
| `prgenv-gnu/25.6:v2` | 8.1.32 | 3.4a2 |
| `prgenv-gnu/24.7:v3` | 8.1.30 | 3.4a2 |

## Environment variables

Cray MPICH reads the `MPICH_*` family. [Environment variables][ref-envvars-mpich] lists this family.
The variables that matter most for the netstack are `MPICH_GPU_SUPPORT_ENABLED`, `MPICH_OFI_NIC_POLICY` and `MPICH_SMP_SINGLE_COPY_MODE`. `MPICH_GPU_SUPPORT_ENABLED` needs [cray-gtl][ref-pkg-cray-gtl].

!!! tip "Start a diagnosis by printing the settings"
    Set `MPICH_ENV_DISPLAY=1` to print every MPICH variable and its value at startup. This shows the resolved value of each default, not only the variables you set.

## Related

* [cray-gtl][ref-pkg-cray-gtl] provides the GPU transport layer for GPU-aware MPI.
* [libfabric][ref-pkg-libfabric] is the fabric that MPI runs over.
* [cray-pmi][ref-pkg-cray-pmi] handles process management and job wire-up.
* [xpmem][ref-pkg-xpmem] provides intra-node single-copy shared memory.
* [mpich][ref-pkg-mpich] and [openmpi][ref-pkg-openmpi] are the alternatives.
