[](){#ref-pkg-cxi-driver}
# cxi-driver

`cxi-driver` is the Linux kernel driver for the HPE Cray Cassini and Slingshot high-speed NIC. It also includes the driver headers.
It is at the bottom of the Slingshot software stack.

| Property | Value |
|---|---|
| Spack package | `cxi-driver` |
| Layer | Slingshot (kernel) |
| Provided by | System, as a kernel module. The headers also appear in user builds. |
| User-buildable | Headers only. A user cannot install the kernel module. |
| Slingshot component | Yes. |
| Upstream | <https://github.com/HewlettPackard/shs-cxi-driver> |

## What it is

`cxi-driver` provides the Linux driver headers for the Cassini 1 and 2 interconnect (Slingshot) and for its Ethernet driver.
The running OS loads the kernel module. It exposes the NIC to user space as `/dev/cxi0` through `/dev/cxiN` and `/sys/class/cxi/cxiN`.
[libcxi][ref-pkg-libcxi] opens those devices. Nothing above libcxi touches the driver directly.

Because it is a kernel module, it is inseparable from the running kernel.
This is the clearest example of a component that a uenv or a container can never replace.
A user build can contain only the driver headers. To compile [libcxi][ref-pkg-libcxi] against the correct ABI, the build requires these headers.

## System or user

System
:   The kernel module ships in the OS image.
    The headers come from the RPM `cray-cxi-driver-devel`, version `1.0.0` in `SHS13.1.0`. The prefix is `/usr`.

User, at build time only
:   A uenv that builds its own [libcxi][ref-pkg-libcxi] pulls in `cxi-driver` headers as a build dependency.
    `prgenv-gnu/25.11` has a `cxi-driver-git.…_main` entry in its store for this reason.
    These headers have no runtime footprint, because there is no `cxi-driver` library to load.

## Identifying it

```console title="Checking for the CXI devices and the system headers"
$ ls /dev/cxi*
$ ls /sys/class/cxi*
$ rpm -q cray-cxi-driver-devel
```

[`system-stack`][ref-tools-system-stack] reports `cxi-driver` from the RPM database.
[`user-stack`][ref-tools-user-stack] does not list it as a runtime component. This is correct, because it is a kernel driver, not a linked library.

## Compatibility

A user-provided [libcxi][ref-pkg-libcxi] can be built against newer [cassini-headers][ref-pkg-cassini-headers]. It still drives the host kernel module.
A mismatch between libcxi and the driver is a candidate netstack diagnosis. That is why this page documents this component, even though it never appears in `ldd`.

## Related

* [libcxi][ref-pkg-libcxi] is the user-space library that opens the CXI devices.
* [cassini-headers][ref-pkg-cassini-headers] provides the hardware and ABI headers shared with the driver.
* [libfabric][ref-pkg-libfabric] contains the OFI provider that ultimately drives the NIC.
