[](){#ref-pkg-libcxi}
# libcxi

libcxi is the user-space library that talks directly to the Slingshot CXI kernel driver. The [libfabric][ref-pkg-libfabric] `cxi` provider builds on top of it.

| Property | Value |
|---|---|
| Spack package | `libcxi` |
| Layer | Slingshot (CXI) |
| Provided by | User or system. |
| User-buildable | Yes. |
| Slingshot component | Yes. |
| Upstream | <https://github.com/HewlettPackard/shs-libcxi> |

## What it is

libcxi, as `libcxi.so.1`, provides the interfaces that interact directly with the CXI drivers. These interfaces cover allocation of communication resources on the NIC, memory registration, and counters.
The [libfabric CXI provider][ref-pkg-libfabric] links it. So do [aws-ofi-nccl][ref-pkg-aws-ofi-nccl] and, transitively, [Cray MPICH][ref-pkg-cray-mpich].

!!! warning "User-space does not mean decoupled from the system"
    Because libcxi speaks to the kernel [cxi-driver][ref-pkg-cxi-driver], a user-provided libcxi must be compatible with the driver in the running kernel.

## System or user

System
:   `/usr/lib64/libcxi.so.1`, from the RPM `cray-libcxi` version `1.0.2` in `SHS13.1.0`.
    This is the default. The system uses it whenever a uenv does not ship its own copy.

User
:   A uenv can build libcxi against [cassini-headers][ref-pkg-cassini-headers] and the [cxi-driver][ref-pkg-cxi-driver] headers, and place it on the view path.
    `prgenv-gnu/25.11` does this.

## Identifying it

| Environment | Version | SHS | Origin | Found via |
|---|---|---|---|---|
| `prgenv-gnu/26.3:v1` | 1.5.0 | 13.0.0 | uenv | rpath |
| `prgenv-gnu/25.11:v1` | 1.5.0 | - | uenv | rpath |
| `prgenv-gnu/25.6:v2` | 1.0.2 | 13.1.0 | rpm | default path |
| `prgenv-gnu/24.7:v3` | 1.0.2 | 13.1.0 | rpm | default path |

The origin of the library decides which version numbers [`user-stack`][ref-tools-user-stack] can report.
A uenv copy takes its version from its soname, `1.5.0`. The tag that its Spack package was built from places it on the SHS timeline. For example, `prgenv-gnu/26.3` used `release/shs-13.0.0` and reports `13.0.0`, while `prgenv-gnu/25.11` used an untagged commit, so the tool can place it nowhere on the timeline.
A host copy is the RPM `cray-libcxi`. It reports the RPM version and the release from the same database that [`system-stack`][ref-tools-system-stack] reads, and the two tools agree on this value exactly.

!!! note "Several version numbers for one library"
    The soname is `1.5.0` in all four environments above, including those built from different SHS releases. So the soname distinguishes none of them.
    The RPM calls the same object `1.0.2`, from `cray-libcxi-1.0.2-SHS13.1.0`.
    All of these numbers are correct. They are different numbering schemes for one library.
    Compare by path or by SHS release, and not across schemes.

## Related

* [cxi-driver][ref-pkg-cxi-driver] is the kernel driver that this library drives.
* [cassini-headers][ref-pkg-cassini-headers] provides the hardware and ABI headers used to build it.
* [libfabric][ref-pkg-libfabric] contains the OFI provider built on top of libcxi.
