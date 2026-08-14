# cuda

> The CUDA toolkit — the runtime (`libcudart`) and libraries that GPU-aware
> netstack components link against. **User** half of the CUDA split.

|  |  |
|---|---|
| Spack package | `cuda` |
| Layer | GPU runtime |
| Provided by | **user** |
| User-buildable | yes (redistributed by NVIDIA) |
| Slingshot component | — |
| Upstream | <https://developer.nvidia.com/cuda-zone> |

## What it is

`cuda` is the CUDA toolkit: the runtime library `libcudart.so`, the compiler,
and the math/comm libraries. In the netstack it is the GPU half that
[cray-gtl][cray-gtl], [NCCL][nccl] and [aws-ofi-nccl][aws-ofi-nccl] link to move
device data.

!!! important "`cuda` vs `cuda-driver` — do not conflate them"
    CUDA is deliberately **two** packages:

    - **`cuda`** (this page) — the *runtime/toolkit* (`libcudart.so.N`). Lives in
      the **uenv**, versioned independently of the OS.
    - **[`cuda-driver`][cuda-driver]** — the *driver* stub (`libcuda.so.1`).
      Comes from the **host**, matched to the kernel.

    Saying "CUDA is host-provided" is wrong — only the driver stub is. A uenv can
    ship any toolkit version compatible with the host driver.

## System vs. user

A **user** component: the toolkit ships in the uenv and appears on the view path
(`CUDA_HOME` points into the view). It requires a compatible host
[CUDA driver][cuda-driver].

## Identifying it

`bin/user-stack` reports the toolkit from the resolved `libcudart` store path:

| Environment | CUDA toolkit | Found via |
|---|---|---|
| `prgenv-gnu/25.11:v1` | 12.9.0 | rpath (uenv) |
| `prgenv-gnu/25.6:v2`  | 12.9.0 | rpath (uenv) |
| `prgenv-gnu/24.7:v3`  | 12.4.0 | rpath (uenv) |

- `libcudart.so.<major>` soname only gives the major; the Spack store directory
  (`cuda-12.9.0-…`) gives the full version.
- Compare against the host driver's max supported CUDA (from `nvidia-smi`) to
  confirm compatibility — see [cuda-driver][cuda-driver].

## Environment variables

`CUDA_*` — notably `CUDA_VISIBLE_DEVICES` (GPU↔NIC affinity) and `CUDA_HOME`.
See [Environment variables][envvars].

## Related

- [cuda-driver][cuda-driver] — the system driver half.
- [cray-gtl][cray-gtl] · [nccl][nccl] · [aws-ofi-nccl][aws-ofi-nccl] — GPU-aware
  consumers.

[cuda-driver]: cuda-driver.md
[cray-gtl]: cray-gtl.md
[nccl]: nccl.md
[aws-ofi-nccl]: aws-ofi-nccl.md
[envvars]: ../envvars.md
