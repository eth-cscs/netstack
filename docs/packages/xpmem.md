[](){#ref-pkg-xpmem}
# xpmem

XPMEM is a Linux kernel module for intra-node shared memory.
It lets one process map another's address space. This enables single-copy MPI transfers within a node.

| Property | Value |
|---|---|
| Spack package | `xpmem` |
| Layer | Intra-node shared memory |
| Provided by | System, as a kernel module. Users can build the userspace library. |
| User-buildable | The userspace library yes, the kernel module no, because it must match the host. |
| Slingshot component | No. |
| Upstream | <https://github.com/hpc/xpmem> |

## What it is

XPMEM lets a process map the memory of another process into its own virtual address space.
[Cray MPICH][ref-pkg-cray-mpich] uses it as the single-copy transport for large intra-node messages. Set `MPICH_SMP_SINGLE_COPY_MODE=XPMEM` to select it. This avoids the double copy through a shared-memory buffer.
It is the intra-node counterpart to the fabric. Traffic that stays on a node goes through XPMEM. Traffic that leaves a node goes through [libfabric][ref-pkg-libfabric].

Like the [CXI driver][ref-pkg-cxi-driver], XPMEM has a kernel-module half that matches the running kernel. You cannot replace this half from user space.
The userspace `libxpmem.so` is a thin shim over it.

## System or user

XPMEM is a system component.
On Alps, the module and `libxpmem.so` come from the host at `/opt/xpmem`. They come from the RPMs `xpmem` and `cray-libxpmem-devel`, version `1.0.1`.
[`user-stack`][ref-tools-user-stack] resolves `libxpmem.so` to the host in all reference uenvs. It finds this through `ld.so.conf`.

## Identifying it

[`system-stack`][ref-tools-system-stack] reports `xpmem` version `1.0.1` from the RPM, with prefix `/opt/xpmem`.
[`user-stack`][ref-tools-user-stack] reports the same `1.0.1`. It shows an `rpm` origin, with `ld.so.conf` as the search mechanism that found it.

!!! note "The version comes from the RPM, not the file"
    The host `libxpmem.so` has the soname `0.0.0`. This is an uninformative libtool soname. It carries no real version.
    `user-stack` asks the RPM database which package owns the file it resolved. It reports the version from there instead.

## Environment variables

`MPICH_SMP_SINGLE_COPY_MODE` selects `XPMEM`, as opposed to `CMA` or `NONE`. [Environment variables][ref-envvars-mpich] lists it.

## Related

* [cray-mpich][ref-pkg-cray-mpich] is the main consumer of XPMEM.
* [libfabric][ref-pkg-libfabric] is the off-node counterpart.
* [cxi-driver][ref-pkg-cxi-driver] is the other host kernel-module component.
