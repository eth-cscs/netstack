# libcxi

> The user-space library that talks directly to the Slingshot **CXI** kernel
> driver. The [libfabric][libfabric] `cxi` provider is built on top of it.

|  |  |
|---|---|
| Spack package | `libcxi` |
| Layer | Slingshot (CXI) |
| Provided by | **user *or* system** |
| User-buildable | yes |
| Slingshot component | ● |
| Upstream | <https://github.com/HewlettPackard/shs-libcxi> |

## What it is

`libcxi` (`libcxi.so.1`) provides the interfaces that interact directly with the
CXI drivers — allocating communication resources on the NIC, memory
registration, counters. The [libfabric CXI provider][libfabric] links it; so do
[aws-ofi-nccl][aws-ofi-nccl] and, transitively, [Cray MPICH][cray-mpich].

Because it speaks to the kernel [`cxi-driver`][cxi-driver], a user-provided
`libcxi` must still be compatible with the **driver in the running kernel** — it
is user-space, but not decoupled from the system.

## System vs. user

- **System.** `/usr/lib64/libcxi.so.1`, RPM `cray-libcxi`
  (`1.0.2`, `SHS13.1.0`). This is the default and is used whenever a uenv does
  not ship its own.
- **User.** A uenv may build `libcxi` (against [cassini-headers][cassini-headers]
  and the [cxi-driver][cxi-driver] headers) and place it on the view path, as
  `prgenv-gnu/25.11` does.

## Identifying it

| Environment | Version (soname) | Origin | Found via |
|---|---|---|---|
| `prgenv-gnu/25.11:v1` | 1.5.0 | **uenv** | rpath |
| `prgenv-gnu/25.6:v2`  | 1.5.0 | host     | default path |
| `prgenv-gnu/24.7:v3`  | 1.5.0 | host     | default path |

!!! note "Two version numbers for one library"
    `bin/user-stack` reports the **soname** version `1.5.0`
    (`libcxi.so.1.5.0`), while `bin/system-stack` reports the **RPM** version
    `1.0.2` (`cray-libcxi-1.0.2-SHS13.1.0`). Both are correct; they are
    different numbering schemes for the same object. Compare by path or SHS
    release, not by these numbers.

## Related

- [cxi-driver][cxi-driver] — the kernel driver this library drives.
- [cassini-headers][cassini-headers] — hardware/ABI headers used to build it.
- [libfabric][libfabric] — the OFI provider built on top of libcxi.

[libfabric]: libfabric.md
[cxi-driver]: cxi-driver.md
[cassini-headers]: cassini-headers.md
[aws-ofi-nccl]: aws-ofi-nccl.md
[cray-mpich]: cray-mpich.md
