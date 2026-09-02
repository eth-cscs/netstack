[](){#ref-pkg-mpich}
# mpich

MPICH is the reference implementation of the MPI standard. [Cray MPICH][ref-pkg-cray-mpich] derives from MPICH and is ABI-compatible with it.

| Property | Value |
|---|---|
| Spack package | `mpich` |
| Layer | MPI |
| Provided by | User. |
| User-buildable | Yes. |
| Slingshot component | Indirectly, through [libfabric][ref-pkg-libfabric] with the `ch4:ofi` device. |
| Upstream | <https://www.mpich.org> |

## What it is

MPICH is relevant to the netstack for two reasons.

ABI compatibility
:   [Cray MPICH][ref-pkg-cray-mpich] implements the MPICH `3.4a2` ABI. A binary built against upstream `mpich` can run against Cray MPICH. A binary built against Cray MPICH can also run against upstream `mpich`.
    This is why [`user-stack`][ref-tools-user-stack] reports the role as "ABI-compatible MPICH".

An alternative MPI
:   You can build `mpich` with the `ch4:ofi` device against [libfabric][ref-pkg-libfabric] and the CXI provider. You can then run it over Slingshot without Cray MPICH.
    On Alps, the Cray build has better fabric tuning, so it is the default choice.

## System or user

When it is present, `mpich` is always a user component.

The `prgenv-gnu` uenvs use [Cray MPICH][ref-pkg-cray-mpich] rather than upstream `mpich`.
This page documents the package for completeness, and for environments that choose it.

## Identifying it

`mpichversion` distinguishes the two builds.
A Cray build reports Cray-specific configure flags and a `GTL-built-with` custom string. A plain build does not report these.

If the MPI library resolves to a Spack store directory named `mpich-*` rather than `cray-mpich-*`, it is upstream MPICH.

## Related

* [cray-mpich][ref-pkg-cray-mpich] is the Cray-tuned derivative, and the default on Alps.
* [openmpi][ref-pkg-openmpi] is the other MPI family.
* [libfabric][ref-pkg-libfabric] is the fabric that a `ch4:ofi` build runs over.
