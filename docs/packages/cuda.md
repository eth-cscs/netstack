[](){#ref-pkg-cuda}
# cuda

The CUDA toolkit provides the runtime, `libcudart`, and the libraries that the GPU-aware netstack components link against.
It is the user half of the CUDA split.

| Property | Value |
|---|---|
| Spack package | `cuda` |
| Layer | GPU runtime |
| Provided by | User. |
| User-buildable | Yes, from the redistribution by NVIDIA. |
| Slingshot component | No. |
| Upstream | <https://developer.nvidia.com/cuda-zone> |

## What it is

`cuda` is the CUDA toolkit: the runtime library `libcudart.so`, the compiler, and the mathematics and communication libraries.
In the netstack it is the GPU half that [cray-gtl][ref-pkg-cray-gtl], [NCCL][ref-pkg-nccl] and [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] link in order to move device data.

!!! warning "`cuda` and `cuda-driver` are not the same thing"
    CUDA is deliberately split across two packages.
    `cuda`, this page, is the runtime and toolkit, `libcudart.so.N`, which lives in the uenv and is versioned independently of the OS.
    [`cuda-driver`][ref-pkg-cuda-driver] is the driver stub, `libcuda.so.1`, which comes from the host and is matched to the kernel.
    Only the driver stub is host-provided, so "CUDA is host-provided" is wrong.
    A uenv can ship any toolkit version that is compatible with the host driver.

## System or user

`cuda` is a user component.
The toolkit ships in the uenv and appears on the view path, with `CUDA_HOME` pointing into the view.
It requires a compatible host [CUDA driver][ref-pkg-cuda-driver].

## Identifying it

[`user-stack`][ref-tools-user-stack] reports the toolkit from the resolved `libcudart` store path.

| Environment | Toolkit version | Found via |
|---|---|---|
| `prgenv-gnu/25.11:v1` | 12.9.0 | rpath, in the uenv |
| `prgenv-gnu/25.6:v2` | 12.9.0 | rpath, in the uenv |
| `prgenv-gnu/24.7:v3` | 12.4.0 | rpath, in the uenv |

The `libcudart.so.<major>` soname gives only the major version, while the Spack store directory, for example `cuda-12.9.0-…`, gives the full version.
Compare that against the maximum CUDA version that the host driver supports, which `nvidia-smi` reports, to confirm compatibility.

## Environment variables

The `CUDA_*` family is listed under [Environment variables][ref-envvars-cuda].
The two that matter most here are `CUDA_VISIBLE_DEVICES`, which affects GPU-to-NIC affinity, and `CUDA_HOME`.

## Related

* [cuda-driver][ref-pkg-cuda-driver] is the system half of the split.
* [cray-gtl][ref-pkg-cray-gtl], [nccl][ref-pkg-nccl] and [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] are the GPU-aware consumers.
