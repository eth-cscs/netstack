# Analysing a uenv

This page documents how the netstack of a **uenv** is extracted. It is
deliberately uenv-specific: the runtime-resolution method is general, but the
package-metadata half relies on the **Spack database** that a uenv ships.
Container and Python-environment support will be documented separately.

A uenv is a SquashFS image that is a **Spack installation whose root is the
mount point** (`/user-environment` by default). That gives us two independent
sources of truth, which the tools combine.

## 1. Mount and view discovery

A loaded uenv exposes itself through the environment:

| Variable | Tells us |
|---|---|
| `UENV_VIEW` = `<mount>:<name>:<view>` | mount point, uenv name, active view |
| `UENV_MOUNT_LIST` = `<sqfs>:<mount>,…` | the mounted image(s) and mount point(s) |
| `UENV_TELEMETRY` | JSON: label, name, mount, views, image digest |

The active **view** (`<mount>/env/<view>/{bin,lib,lib64}`) is what rewrites
`PATH` / `LD_LIBRARY_PATH`, so it is the starting point for finding the
libraries that are actually in play.

## 2. Runtime resolution — what actually loads

Starting from *anchor* libraries on the view path (the MPI library, `libnccl`,
the aws-ofi-nccl plugin), we resolve the full dependency tree with
[`libtree`](https://github.com/haampie/libtree):

```console
$ libtree -p /user-environment/env/default/lib/libmpi_gnu_123.so.12
```

`libtree -p` is preferred over `ldd` because it:

- resolves ELF dependencies **statically** — it does not execute the object;
- annotates **how** each library was found: `[rpath]`, `[runpath]`,
  `[LD_LIBRARY_PATH]`, `[default path]`, `[ld.so.conf]`.

That "how" is real signal. In `prgenv-gnu/25.6`, Cray MPICH is **rpath-pinned**
to `/opt/cray/libfabric/1.22.0` — *not* the system-default libfabric — and only
the resolved path and its search mechanism reveal it. `bin/user-stack` surfaces
this in its **Found via** column, falling back to `ldd` (losing only the
annotation) if `libtree` is absent.

### Provenance by path

Provenance is **never** guessed from a library's name. For each resolved
dependency we take its real path and test whether it lies under the uenv mount:

- under `<mount>` → **uenv**-provided;
- elsewhere (`/usr/lib64`, `/opt/cray/...`, `/opt/xpmem`) → **host**-provided.

The same library lands on either side depending on the environment:
[libfabric][libfabric] and [libcxi][libcxi] are uenv-provided in
`prgenv-gnu/25.11` but host-provided in `25.6` and `24.7`.

## 3. The Spack database — identity and build graph

Runtime resolution finds *paths*; the Spack database says what those paths
**are**. Every installed package is recorded in:

```
<mount>/.spack-db/index.json
```

Each entry carries the package name, version, install prefix, dag-hash, and its
dependency edges tagged `build` / `link` / `run`. This is the **source of truth
for dependencies**, and it exposes two things runtime resolution cannot:

- **Authoritative identity.** A resolved store path
  `…/libfabric-2.3.1-ekke44pq…/` maps by its trailing hash to the exact package
  record. `bin/user-stack` attaches this hash to every uenv component.
- **Build-only dependencies.** Packages that produce no runtime `.so` — most
  importantly the Slingshot [cassini-headers][cassini-headers] and
  [cxi-driver][cxi-driver] headers — appear in the graph but never in `ldd`.

!!! warning "The database is *build-time* truth, not runtime truth"
    The database describes what the uenv was **built against**. For **external**
    packages it can diverge from what loads: on Alps the Spack `xpmem` external
    is recorded as `2.9.6` under `/usr`, while the library that actually loads is
    the host `/opt/xpmem` copy (RPM `1.0.1`). So: trust the database for the
    identity of **in-uenv** packages and for **build** dependencies; trust
    runtime resolution for what host libraries actually load.

### Build provenance

Combining the two sources answers a question central to diagnosis: **what NIC
ABI was the fabric stack built against?** For each uenv-provided
[libfabric][libfabric] / [libcxi][libcxi], `bin/user-stack` reports the
[cassini-headers][cassini-headers] and [cxi-driver][cxi-driver] versions from
the database — then those can be checked against the **host** kernel
[cxi-driver][cxi-driver] (from `bin/system-stack`). In `prgenv-gnu/25.11` the
fabric libraries are built against git-`main` Cassini headers while the host
driver is `1.0.0 (SHS13.1.0)` — exactly the kind of pairing a compatibility
check must reason about.

## 4. Version namespaces — a caveat

Different sources report different **numbering schemes** for one library; a
mismatch between them is expected, not a bug:

| Source | Example (libcxi) | What it is |
|---|---|---|
| RPM (`system-stack`) | `1.0.2` (`SHS13.1.0`) | host package version |
| soname (`user-stack`) | `1.5.0` (`libcxi.so.1.5.0`) | shared-object / ABI version |
| Spack db | `git.be1f7149…=main` | the commit the uenv built |

All three are correct. Compare like with like — by path, hash, or SHS release —
not across schemes.

## Querying the database directly

`bin/spack-db` exposes the database for ad-hoc queries (see [Tools][tools]):

```console
$ M=/user-environment
$ spack-db --mount $M list --name libfabric     # installed libfabrics
$ spack-db --mount $M show libfabric             # package + direct deps (with deptypes)
$ spack-db --mount $M deps libfabric --type link -t   # transitive link dependencies
$ spack-db --mount $M dependents libcxi          # what needs libcxi
$ spack-db --mount $M owner <path-to-a-.so>      # which package owns a path
```

A package is named by full hash, unique hash prefix, or name. **`--mount` is
required** and names the Spack install root (the uenv mount point, from
`$UENV_MOUNT`); it may be given before or after the subcommand.

[libfabric]: ../packages/libfabric.md
[libcxi]: ../packages/libcxi.md
[cassini-headers]: ../packages/cassini-headers.md
[cxi-driver]: ../packages/cxi-driver.md
[tools]: ../tools.md
