# cxi-driver

> The Linux kernel driver (and its headers) for the HPE Cray **Cassini /
> Slingshot** high-speed NIC. The bottom of the Slingshot software stack.

|  |  |
|---|---|
| Spack package | `cxi-driver` |
| Layer | Slingshot (kernel) |
| Provided by | **system** (kernel module); headers also in user builds |
| User-buildable | headers only — the kernel module is **not** user-installable |
| Slingshot component | ● |
| Upstream | <https://github.com/HewlettPackard/shs-cxi-driver> |

## What it is

`cxi-driver` provides the Linux driver headers for the Cassini 1/2 interconnect
(Slingshot) and its Ethernet driver. The **kernel module** itself is loaded in
the running OS and exposes the NIC to user space as `/dev/cxi0…N` and
`/sys/class/cxi/cxiN`. [libcxi][libcxi] opens these devices; nothing above it
touches the driver directly.

Because it is a kernel module, it is **inseparable from the running kernel** —
this is the canonical example of a component that a uenv or container can never
replace. What a user build *can* contain is the driver **headers**, needed to
compile [libcxi][libcxi] against the correct ABI.

## System vs. user

- **System.** The kernel module ships in the OS image. Headers: RPM
  `cray-cxi-driver-devel` (`1.0.0`, `SHS13.1.0`), prefix `/usr`.
- **User (build-time only).** A uenv that builds its own [libcxi][libcxi] pulls
  in `cxi-driver` headers as a build dependency. `prgenv-gnu/25.11` has a
  `cxi-driver-git.…_main` entry in its store for exactly this reason. These
  headers have **no runtime footprint** — there is no `cxi-driver` library to
  load.

## Identifying it

- Hardware present → `ls /dev/cxi*`, `ls /sys/class/cxi*`.
- System headers → `rpm -q cray-cxi-driver-devel`.
- The running module → `bin/system-stack` reports `cxi-driver` from the RPM.
- `bin/user-stack` does **not** list it as a runtime component (correctly — it
  is a kernel driver, not a linked library).

## Compatibility note

A user-provided [libcxi][libcxi] built against newer
[cassini-headers][cassini-headers] still drives the **host kernel module**. A
libcxi/driver mismatch is a candidate netstack diagnosis (phase 2), and the
reason this component is documented even though it never appears in `ldd`.

## Related

- [libcxi][libcxi] — the user-space library that opens the CXI devices.
- [cassini-headers][cassini-headers] — the hardware/ABI headers shared with the driver.
- [libfabric][libfabric] — the OFI provider that ultimately drives the NIC.

[libcxi]: libcxi.md
[cassini-headers]: cassini-headers.md
[libfabric]: libfabric.md
