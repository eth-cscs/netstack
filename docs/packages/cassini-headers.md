[](){#ref-pkg-cassini-headers}
# cassini-headers

`cassini-headers` holds the hardware definitions and C headers for the Cassini, that is Slingshot, NIC, and they are shared by the kernel driver, by [libcxi][ref-pkg-libcxi] and by the [libfabric][ref-pkg-libfabric] CXI provider.

| Property | Value |
|---|---|
| Spack package | `cassini-headers` |
| Layer | Slingshot (headers) |
| Provided by | System and user, at build time. |
| User-buildable | Yes, headers only. |
| Slingshot component | Yes. |
| Upstream | <https://github.com/HewlettPackard/shs-cassini-headers> |

## What it is

`cassini-headers` is a headers-only package containing hardware register definitions and C ABI headers for the HPE Cassini high-speed interconnect.
It is consumed at build time by everything in the Slingshot stack that needs to know the NIC ABI, namely the [cxi-driver][ref-pkg-cxi-driver], [libcxi][ref-pkg-libcxi] and the CXI provider inside [libfabric][ref-pkg-libfabric].

It has no runtime library and never appears in a dependency tree.
It matters because the header version that a component was built against defines the NIC ABI that the component expects.

## System or user

System
:   The RPM `cray-cassini-headers-user`, version `1.1.2` in `SHS13.1.0`, with prefix `/usr`.
    These are used when building against the system Slingshot stack.

User, at build time
:   A uenv that builds its own [libcxi][ref-pkg-libcxi] or [libfabric][ref-pkg-libfabric] pins a `cassini-headers` version.
    `prgenv-gnu/25.11` carries a `cassini-headers-git.…_main` store entry.

## Identifying it

```console title="Checking the system headers"
$ rpm -q cray-cassini-headers-user
```

[`system-stack`][ref-tools-system-stack] reports `cassini-headers` together with its SHS release.
In a uenv build the headers appear as a `cassini-headers-*` directory in the Spack store, as a build dependency, but nothing appears on `LD_LIBRARY_PATH`.
[Build provenance][ref-analysis-uenv-build-provenance] describes how to compare the headers a library was built against with the host driver.

## Related

* [cxi-driver][ref-pkg-cxi-driver] is the kernel driver built from the same ABI.
* [libcxi][ref-pkg-libcxi] is the user-space library built against these headers.
* [libfabric][ref-pkg-libfabric] contains the CXI provider built against these headers.
