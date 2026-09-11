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

The CUDA driver is always a system component, and both tools report it as one, each finding it a different way.
[`system-stack`][ref-tools-system-stack] has no dependency tree to walk, so it looks up the well-known path of the driver's userspace library, `/usr/lib64/libcuda.so.1`, and asks the RPM database who owns it — the same kind of simple, name-agnostic lookup [`cxi-driver`][ref-pkg-cxi-driver] needs on the system side.
[`user-stack`][ref-tools-user-stack] resolves the same library by walking a uenv's resolved dependency tree, and finds it under `/usr/lib64`. The origin is host, never under the uenv mount.
That is the correct and expected result, and the two reports agree field by field: same version, same owning package, same prefix.

## Identifying it

```console title="Reading the driver version and its maximum CUDA version"
$ nvidia-smi --version
```

On the reference node, the driver is `590.48.01`, and the maximum CUDA version is `13.1`. So a uenv toolkit in the `12.x` series runs against it.
[`system-stack`][ref-tools-system-stack] reports the driver version as the `cuda-driver` component, and the maximum CUDA version as the `max-cuda-version` property.

!!! note "Two numbers called CUDA"
    `max-cuda-version`, read from `nvidia-smi`, for example `13.1`, is the maximum that the driver supports.
    The [CUDA toolkit][ref-pkg-cuda] version in the uenv, for example `12.9.0`, is the version your code links against.
    The first is the maximum allowed, and the second is the actual version in use.

## Related

* [cuda][ref-pkg-cuda] is the user-provided toolkit that runs against this driver.
* [cxi-driver][ref-pkg-cxi-driver] is the analogous host kernel driver for Slingshot.
