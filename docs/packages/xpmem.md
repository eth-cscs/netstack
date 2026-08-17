[](){#ref-pkg-xpmem}
# xpmem

XPMEM is a Linux kernel module for intra-node shared memory.
It lets one process map another's address space, which enables single-copy MPI transfers within a node.

| Property | Value |
|---|---|
| Spack package | `xpmem` |
| Layer | Intra-node shared memory |
| Provided by | System, as a kernel module. The userspace library can be user-built. |
| User-buildable | The userspace library yes, the kernel module no, because it must match the host. |
| Slingshot component | No. |
| Upstream | <https://github.com/hpc/xpmem> |

## What it is

XPMEM lets a process map the memory of another process into its own virtual address space.
[Cray MPICH][ref-pkg-cray-mpich] uses it as the single-copy transport for large intra-node messages, selected with `MPICH_SMP_SINGLE_COPY_MODE=XPMEM`, which avoids the double copy through a shared-memory buffer.
It is the intra-node counterpart to the fabric: traffic that stays on a node goes through XPMEM, and traffic that leaves a node goes through [libfabric][ref-pkg-libfabric].

Like the [CXI driver][ref-pkg-cxi-driver], XPMEM has a kernel module half that is tied to the running kernel and cannot be replaced from user space.
The userspace `libxpmem.so` is a thin shim over it.

## System or user

XPMEM is effectively a system component.
On Alps the module and `libxpmem.so` come from the host at `/opt/xpmem`, from the RPMs `xpmem` and `cray-libxpmem-devel`, version `1.0.1`.
[`user-stack`][ref-tools-user-stack] resolves `libxpmem.so` to the host, found through `ld.so.conf`, in all of the reference uenvs.

## Identifying it

[`system-stack`][ref-tools-system-stack] reports `xpmem` version `1.0.1` from the RPM, with prefix `/opt/xpmem`.
[`user-stack`][ref-tools-user-stack] shows `xpmem` as host-provided, and reports no version.

!!! note "The blank version is deliberate"
    The host `libxpmem.so` has the soname `0.0.0`, which is an uninformative libtool soname carrying no real version.
    Rather than print `0.0.0`, `user-stack` leaves the field blank and defers to the RPM version from `system-stack`.

## Environment variables

`MPICH_SMP_SINGLE_COPY_MODE` selects `XPMEM`, as opposed to `CMA` or `NONE`, and is listed under [Environment variables][ref-envvars-mpich].

## Related

* [cray-mpich][ref-pkg-cray-mpich] is the main consumer of XPMEM.
* [libfabric][ref-pkg-libfabric] is the off-node counterpart.
* [cxi-driver][ref-pkg-cxi-driver] is the other host kernel-module component.
