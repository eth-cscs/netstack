[](){#ref-pkg-libcxi}
# libcxi

libcxi is the user-space library that talks directly to the Slingshot CXI kernel driver, and the [libfabric][ref-pkg-libfabric] `cxi` provider is built on top of it.

| Property | Value |
|---|---|
| Spack package | `libcxi` |
| Layer | Slingshot (CXI) |
| Provided by | User or system. |
| User-buildable | Yes. |
| Slingshot component | Yes. |
| Upstream | <https://github.com/HewlettPackard/shs-libcxi> |

## What it is

libcxi, as `libcxi.so.1`, provides the interfaces that interact directly with the CXI drivers, covering allocation of communication resources on the NIC, memory registration and counters.
The [libfabric CXI provider][ref-pkg-libfabric] links it, and so do [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] and, transitively, [Cray MPICH][ref-pkg-cray-mpich].

!!! warning "User-space does not mean decoupled from the system"
    Because libcxi speaks to the kernel [cxi-driver][ref-pkg-cxi-driver], a user-provided libcxi still has to be compatible with the driver in the running kernel.

## System or user

System
:   `/usr/lib64/libcxi.so.1`, from the RPM `cray-libcxi` version `1.0.2` in `SHS13.1.0`.
    This is the default, and it is used whenever a uenv does not ship its own copy.

User
:   A uenv can build libcxi, against [cassini-headers][ref-pkg-cassini-headers] and the [cxi-driver][ref-pkg-cxi-driver] headers, and place it on the view path.
    `prgenv-gnu/25.11` does this.

## Identifying it

| Environment | Version (soname) | Origin | Found via |
|---|---|---|---|
| `prgenv-gnu/25.11:v1` | 1.5.0 | uenv | rpath |
| `prgenv-gnu/25.6:v2` | 1.5.0 | host | default path |
| `prgenv-gnu/24.7:v3` | 1.5.0 | host | default path |

!!! note "Two version numbers for one library"
    [`user-stack`][ref-tools-user-stack] reports the soname version `1.5.0`, from `libcxi.so.1.5.0`, while [`system-stack`][ref-tools-system-stack] reports the RPM version `1.0.2`, from `cray-libcxi-1.0.2-SHS13.1.0`.
    Both are correct, and they are different numbering schemes for the same object.
    Compare by path or by SHS release, and not by these numbers.

## Related

* [cxi-driver][ref-pkg-cxi-driver] is the kernel driver that this library drives.
* [cassini-headers][ref-pkg-cassini-headers] provides the hardware and ABI headers used to build it.
* [libfabric][ref-pkg-libfabric] contains the OFI provider built on top of libcxi.
