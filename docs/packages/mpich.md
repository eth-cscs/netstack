# mpich

> Upstream MPICH — the reference MPI that [Cray MPICH][cray-mpich] is derived
> from and ABI-compatible with.

|  |  |
|---|---|
| Spack package | `mpich` |
| Layer | MPI |
| Provided by | **user** |
| User-buildable | yes |
| Slingshot component | via [libfabric][libfabric] (with `ch4:ofi`) |
| Upstream | <https://www.mpich.org> |

## What it is

MPICH is the widely-used reference implementation of the MPI standard. It is
relevant to the netstack for two reasons:

1. **ABI compatibility.** [Cray MPICH][cray-mpich] implements the MPICH ABI
   (`3.4a2`), so binaries built against upstream `mpich` can run against Cray
   MPICH and vice-versa. This is why the `user-stack` role line reads
   "ABI-compatible MPICH".
2. **As an alternative MPI.** A user can build `mpich` with the `ch4:ofi`
   device against [libfabric][libfabric]/CXI and run over Slingshot without Cray
   MPICH — though on Alps the Cray build is preferred for fabric tuning.

## System vs. user

Always a **user** component when present. The prgenv-gnu uenvs use
[Cray MPICH][cray-mpich], not upstream `mpich`; this page documents the package
for completeness and for environments that choose it.

## Identifying it

- `mpichversion` distinguishes builds. A Cray build reports Cray-specific
  configure flags and a `GTL-built-with` custom string; a plain build does not.
- If the MPI library resolves to a `mpich-*` (not `cray-mpich-*`) Spack store
  directory, it is upstream MPICH.

## Related

- [cray-mpich][cray-mpich] — the Cray-tuned derivative (default on Alps).
- [openmpi][openmpi] — the other MPI family.
- [libfabric][libfabric] — the fabric an `ch4:ofi` build runs over.

[cray-mpich]: cray-mpich.md
[openmpi]: openmpi.md
[libfabric]: libfabric.md
