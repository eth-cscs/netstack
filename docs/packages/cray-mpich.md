# cray-mpich

> HPE Cray's MPICH — the default, Slingshot-tuned MPI implementation on Alps.

|  |  |
|---|---|
| Spack package | `cray-mpich` |
| Layer | MPI |
| Provided by | **user** (uenv / module) |
| User-buildable | no — redistributed binary from HPE |
| Slingshot component | via [libfabric][libfabric] |
| Upstream | <https://docs.nersc.gov/development/compilers/wrappers/> |

## What it is

Cray MPICH is a high-performance MPI derived from [MPICH][mpich] and tuned for
the Slingshot fabric. It is **ABI-compatible with MPICH** (`3.4a2`, device
`ch4:ofi`), so applications built against upstream MPICH run against it
unchanged. It reaches the network through [libfabric][libfabric]/CXI and, for
GPU-aware transfers, through [cray-gtl][cray-gtl].

The compiler wrappers `mpicc` / `mpicxx` / `mpifort` on the view `PATH` wrap the
uenv's GCC. `mpicc -show` reveals the link line (`-lmpi_gnu_123 -lmpi_gtl_cuda
…`); `mpichversion` prints the full build configuration.

### Runtime dependencies

From the MPI library's dependency tree:

```
libmpi_gnu_123 → libmpi_gtl_cuda   (GPU-aware, cray-gtl)
              → libfabric.so.1     → libcxi.so.1 → Slingshot NIC
              → libpmi / libpmi2   (cray-pmi, launch/wire-up)
              → libxpmem           (intra-node shared memory)
              → libcudart / libcuda
```

## System vs. user

Cray MPICH is a **user** component: it comes from the uenv (or a `cray-mpich`
module), and appears directly on the view path. Its *dependencies*, however, may
be host- or uenv-provided — notably [libfabric][libfabric] and [libcxi][libcxi]
(see those pages).

## Identifying it

`bin/user-stack` reports the `cray-mpich` package version and the ABI-compatible
MPICH base:

| Environment | cray-mpich | MPICH base |
|---|---|---|
| `prgenv-gnu/25.11:v1` | 8.1.32 | 3.4a2 |
| `prgenv-gnu/25.6:v2`  | 8.1.32 | 3.4a2 |
| `prgenv-gnu/24.7:v3`  | 8.1.30 | 3.4a2 |

## Environment variables

The `MPICH_*` family — see [Environment variables][envvars]. Most important for
the netstack: `MPICH_GPU_SUPPORT_ENABLED` (with [cray-gtl][cray-gtl]),
`MPICH_OFI_NIC_POLICY`, `MPICH_SMP_SINGLE_COPY_MODE`. `MPICH_ENV_DISPLAY=1`
prints every setting at startup — the first thing to turn on when diagnosing.

## Related

- [cray-gtl][cray-gtl] — GPU transport layer for GPU-aware MPI.
- [libfabric][libfabric] — the fabric MPI runs over.
- [cray-pmi][cray-pmi] — process management / job wire-up.
- [xpmem][xpmem] — intra-node single-copy shared memory.
- [mpich][mpich] · [openmpi][openmpi] — the alternatives.

[libfabric]: libfabric.md
[libcxi]: libcxi.md
[cray-gtl]: cray-gtl.md
[cray-pmi]: cray-pmi.md
[xpmem]: xpmem.md
[mpich]: mpich.md
[openmpi]: openmpi.md
[envvars]: ../envvars.md
