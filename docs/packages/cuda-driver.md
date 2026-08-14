# cuda-driver

> The NVIDIA CUDA **driver** — the userspace stub `libcuda.so.1` bound to the
> kernel driver. **System** half of the CUDA split.

|  |  |
|---|---|
| Spack package | `cuda-driver` (logical; not a buildable Spack package) |
| Layer | GPU driver |
| Provided by | **system** |
| User-buildable | no — matched to the running kernel |
| Slingshot component | — |
| Upstream | NVIDIA (installed with the GPU driver) |

## What it is

The CUDA driver is the userspace library `libcuda.so.1` that talks to the NVIDIA
kernel module. It is the GPU analogue of [libcxi][libcxi]/[cxi-driver][cxi-driver]:
a userspace stub that must match the **kernel driver in the running OS**, so it
can never be shipped by a uenv or container.

It exposes a *maximum supported* CUDA version; any [CUDA toolkit][cuda] up to
that version can run against it. This forward-compatibility is exactly why the
toolkit is decoupled into its own [`cuda`][cuda] package.

## System vs. user

Always **system**. `bin/user-stack` resolves `libcuda.so.1` and finds it under
`/usr/lib64` (origin **host**, found via *default path*), never under the uenv
mount — the correct and expected result.

## Identifying it

- `nvidia-smi --version` reports the **driver version** and the max **CUDA
  version** the driver supports.
- On the reference node: driver `590.48.01`, CUDA `13.1` (max). A uenv toolkit of
  `12.x` therefore runs fine.
- `bin/system-stack` surfaces both as the `nvidia-driver` and `cuda` properties.

!!! note
    The `cuda` value from `nvidia-smi` (driver max, e.g. `13.1`) is a *different
    number* from the uenv [CUDA toolkit][cuda] (e.g. `12.9.0`). The first is a
    ceiling; the second is what your code links.

## Related

- [cuda][cuda] — the user-provided toolkit that runs against this driver.
- [cxi-driver][cxi-driver] — the analogous host kernel driver for Slingshot.

[cuda]: cuda.md
[libcxi]: libcxi.md
[cxi-driver]: cxi-driver.md
