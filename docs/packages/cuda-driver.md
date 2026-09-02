[](){#ref-pkg-cuda-driver}
# cuda-driver

The CUDA driver is the userspace stub `libcuda.so.1`. It binds to the NVIDIA kernel driver.
It is the system half of the CUDA split.

| Property | Value |
|---|---|
| Spack package | `cuda-driver`, a logical name rather than a buildable Spack package. |
| Layer | GPU driver |
| Provided by | System. |
| User-buildable | No. It matches the running kernel. |
| Slingshot component | No. |
| Upstream | NVIDIA, installed with the GPU driver. |

## What it is

The CUDA driver is the userspace library `libcuda.so.1`. It talks to the NVIDIA kernel module.
It is the GPU analogue of [libcxi][ref-pkg-libcxi] over [cxi-driver][ref-pkg-cxi-driver]. It is a userspace stub that must match the kernel driver in the running OS. A uenv or a container can never ship it.

The driver exposes a maximum supported CUDA version. Any [CUDA toolkit][ref-pkg-cuda] up to that version can run against it.
This forward compatibility is why the toolkit exists as its own [`cuda`][ref-pkg-cuda] package.

## System or user

The CUDA driver is always a system component.
[`user-stack`][ref-tools-user-stack] resolves `libcuda.so.1` and finds it under `/usr/lib64`. The origin is host, and the tool finds it through the default path, never under the uenv mount.
That is the correct and expected result.

## Identifying it

```console title="Reading the driver version and its maximum CUDA version"
$ nvidia-smi --version
```

On the reference node, the driver is `590.48.01`, and the maximum CUDA version is `13.1`. So a uenv toolkit in the `12.x` series runs against it.
[`system-stack`][ref-tools-system-stack] reports both values, as the `nvidia-driver` and `cuda` properties.

!!! note "Two numbers called CUDA"
    The `cuda` value from `nvidia-smi`, for example `13.1`, is the maximum that the driver supports.
    The [CUDA toolkit][ref-pkg-cuda] version in the uenv, for example `12.9.0`, is the version your code links against.
    The first is the maximum allowed, and the second is the actual version in use.

## Related

* [cuda][ref-pkg-cuda] is the user-provided toolkit that runs against this driver.
* [cxi-driver][ref-pkg-cxi-driver] is the analogous host kernel driver for Slingshot.
