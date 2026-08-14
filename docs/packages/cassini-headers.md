# cassini-headers

> Hardware definitions and C headers for the **Cassini / Slingshot** NIC, shared
> by the kernel driver, [libcxi][libcxi], and the [libfabric][libfabric] CXI
> provider.

|  |  |
|---|---|
| Spack package | `cassini-headers` |
| Layer | Slingshot (headers) |
| Provided by | system + user (build-time) |
| User-buildable | yes (headers only) |
| Slingshot component | ● |
| Upstream | <https://github.com/HewlettPackard/shs-cassini-headers> |

## What it is

`cassini-headers` is a **headers-only** package: hardware register definitions
and C ABI headers for the HPE Cassini high-speed interconnect (Slingshot). It is
consumed at **build time** by everything in the Slingshot stack that needs to
know the NIC ABI — the [cxi-driver][cxi-driver], [libcxi][libcxi], and the CXI
provider inside [libfabric][libfabric].

It has **no runtime library** and never appears in a dependency tree; it matters
because the header version a component was built against defines the NIC ABI
that component expects.

## System vs. user

- **System.** RPM `cray-cassini-headers-user` (`1.1.2`, `SHS13.1.0`), prefix
  `/usr`. Used when building against the system Slingshot stack.
- **User (build-time).** A uenv that builds its own [libcxi][libcxi] /
  [libfabric][libfabric] pins a `cassini-headers` version; `prgenv-gnu/25.11`
  carries a `cassini-headers-git.…_main` store entry.

## Identifying it

- System headers → `rpm -q cray-cassini-headers-user`; `bin/system-stack`
  reports `cassini-headers` and its SHS release.
- In a uenv build → a `cassini-headers-*` directory in the Spack store (build
  dependency), but nothing on `LD_LIBRARY_PATH`.

## Related

- [cxi-driver][cxi-driver] — kernel driver built from the same ABI.
- [libcxi][libcxi] — user-space library built against these headers.
- [libfabric][libfabric] — CXI provider built against these headers.

[cxi-driver]: cxi-driver.md
[libcxi]: libcxi.md
[libfabric]: libfabric.md
