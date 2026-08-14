# xpmem

> A Linux kernel module for **intra-node** shared memory — one process maps
> another's address space, enabling single-copy MPI transfers within a node.

|  |  |
|---|---|
| Spack package | `xpmem` |
| Layer | intra-node shared memory |
| Provided by | **system** (kernel module); userspace lib can be user-built |
| User-buildable | userspace library yes; the kernel module must match the host |
| Slingshot component | — |
| Upstream | <https://github.com/hpc/xpmem> |

## What it is

XPMEM lets a process map the memory of another process into its own virtual
address space. [Cray MPICH][cray-mpich] uses it as the **single-copy** transport
for large intra-node messages (`MPICH_SMP_SINGLE_COPY_MODE=XPMEM`), avoiding the
double copy through a shared-memory buffer. It is the intra-node counterpart to
the fabric: on-node traffic goes through XPMEM, off-node through
[libfabric][libfabric].

Like the [CXI driver][cxi-driver], XPMEM has a **kernel module** half that is
tied to the running kernel and cannot be replaced from user space; the userspace
`libxpmem.so` is a thin shim over it.

## System vs. user

Effectively **system**: on Alps the module and `libxpmem.so` come from the host
at `/opt/xpmem` (RPM `xpmem` / `cray-libxpmem-devel`, `1.0.1`). `bin/user-stack`
resolves `libxpmem.so` to the host (found via *ld.so.conf*) in all reference
uenvs.

## Identifying it

- `bin/system-stack` reports `xpmem` `1.0.1` from the RPM (prefix `/opt/xpmem`).
- `bin/user-stack` shows `xpmem` as **host**-provided. It reports no version,
  because the host `libxpmem.so` soname is `0.0.0` (an uninformative libtool
  soname) — the meaningful version is the RPM one from `system-stack`.

!!! note
    The blank version in `user-stack` is deliberate: an all-zero soname carries
    no real version, so the tool declines to print `0.0.0` and defers to the
    RPM-based value.

## Environment variables

- `MPICH_SMP_SINGLE_COPY_MODE` — selects `XPMEM` (vs `CMA`/`NONE`).

See [Environment variables][envvars].

## Related

- [cray-mpich][cray-mpich] — the main consumer of XPMEM.
- [libfabric][libfabric] — the off-node counterpart.
- [cxi-driver][cxi-driver] — the other host kernel-module component.

[cray-mpich]: cray-mpich.md
[libfabric]: libfabric.md
[cxi-driver]: cxi-driver.md
[envvars]: ../envvars.md
