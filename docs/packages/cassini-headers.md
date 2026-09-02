[](){#ref-pkg-cassini-headers}
# cassini-headers

`cassini-headers` holds the hardware definitions and C headers for the Cassini NIC, that is, the Slingshot NIC.
The kernel driver, [libcxi][ref-pkg-libcxi] and the [libfabric][ref-pkg-libfabric] CXI provider all share these headers.

| Property | Value |
|---|---|
| Spack package | `cassini-headers` |
| Layer | Slingshot (headers) |
| Provided by | System and user, at build time. |
| User-buildable | Yes, headers only. |
| Slingshot component | Yes. |
| Upstream | <https://github.com/HewlettPackard/shs-cassini-headers> |

## What it is

`cassini-headers` is a headers-only package. It contains hardware register definitions and C ABI headers for the HPE Cassini high-speed interconnect.
Every component in the Slingshot stack that must know the NIC ABI consumes these headers at build time. These components are the [cxi-driver][ref-pkg-cxi-driver], [libcxi][ref-pkg-libcxi] and the CXI provider inside [libfabric][ref-pkg-libfabric].

It has no runtime library and never appears in a dependency tree.
It matters because the header version used to build a component defines the NIC ABI that the component expects.

## System or user

System
:   The RPM `cray-cassini-headers-user`, version `1.1.2` in `SHS13.1.0`, with prefix `/usr`.
    You use these when you build against the system Slingshot stack.

User, at build time
:   If a uenv builds its own [libcxi][ref-pkg-libcxi] or [libfabric][ref-pkg-libfabric], it pins a `cassini-headers` version.
    `prgenv-gnu/25.11` carries a `cassini-headers-git.…_main` store entry.

## Identifying it

```console title="Checking the system headers"
$ rpm -q cray-cassini-headers-user
```

[`system-stack`][ref-tools-system-stack] reports `cassini-headers` together with its SHS release.
In a uenv build, the headers appear as a `cassini-headers-*` directory in the Spack store, as a build dependency. Nothing appears on `LD_LIBRARY_PATH`.
[Build provenance][ref-analysis-uenv-build-provenance] describes how to compare the headers used to build a library with the host driver.

## Related

* [cxi-driver][ref-pkg-cxi-driver] is the kernel driver built from the same ABI.
* [libcxi][ref-pkg-libcxi] is the user-space library built against these headers.
* [libfabric][ref-pkg-libfabric] contains the CXI provider built against these headers.
