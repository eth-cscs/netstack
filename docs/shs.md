[](){#ref-shs}
# Slingshot Host Software (SHS)

HPE Slingshot Host Software is the software that HPE ships for the Slingshot interconnect of an HPE Cray EX system.
SHS is a *release bundle* rather than a single package: one SHS version, for example `13.1.0`, names a kernel driver, a set of user-space libraries and a set of headers that were built, tested and released together.

SHS is the axis along which fabric problems are diagnosed, because it is the only number that both halves of the [system/user split][ref-index-user] have in common.
The host runs one SHS release, a uenv is built against another, and a mismatch between the two is the first thing to establish.

!!! note "This page is a working set of notes"
    What we know about SHS is being recorded here as the tooling grows, rather than being written once and left.
    Everything below was observed on `daint` and is dated where it matters.

[](){#ref-shs-contents}
## What is in SHS

The parts of SHS that the netstack tools track are the Slingshot NIC driver and the user-space stack that talks to it.
Each one exists twice: as an RPM in the host OS image, and as a Spack package that a uenv can build for itself.

| Component | Host RPM | Spack package | Upstream repository |
|---|---|---|---|
| [cxi-driver][ref-pkg-cxi-driver] | `cray-cxi-driver-devel` | `cxi-driver` | [shs-cxi-driver](https://github.com/HewlettPackard/shs-cxi-driver) |
| [cassini-headers][ref-pkg-cassini-headers] | `cray-cassini-headers-user` | `cassini-headers` | [shs-cassini-headers](https://github.com/HewlettPackard/shs-cassini-headers) |
| [libcxi][ref-pkg-libcxi] | `cray-libcxi` | `libcxi` | [shs-libcxi](https://github.com/HewlettPackard/shs-libcxi) |
| [libfabric][ref-pkg-libfabric] | `libfabric` | `libfabric` | upstream OFI, with the HPE `cxi` provider |

Not everything in the netstack comes from SHS.
[xpmem][ref-pkg-xpmem], Slurm and Lustre are host software with their own release cycles, and [`system-stack`][ref-tools-system-stack] reports no SHS release for them.

This is what `daint` carried in September 2026, an SHS 13.1.0 host:

| Component | RPM version | SHS | Prefix |
|---|---|---|---|
| cassini-headers | 1.1.2 | 13.1.0 | `/usr` |
| libcxi | 1.0.2 | 13.1.0 | `/usr` |
| cxi-driver | 1.0.0 | 13.1.0 | `/usr` |
| libfabric | 2.3.1 | 13.1.0 | `/opt/cray/libfabric/2.3.1` |

The RPM version and the SHS release are different numbers, and neither can be derived from the other.
`cray-libcxi` is at `1.0.2` inside SHS `13.1.0`, and the soname of the same library is `1.5.0` again.
See [version namespaces][ref-analysis-uenv-version-namespaces] for the full list of numbers that describe one library.

[](){#ref-shs-versions}
## Detecting the SHS version

[](){#ref-shs-versions-host}
### On the host, from the RPM release string

The SHS release is not the RPM version, it is stamped into the RPM *release* field, together with a build timestamp and a short commit:

```
cray-libcxi-1.0.2-SHS13.1.0_20260127170946_9d460216fdc4
                  ^^^^^^^^^ ^^^^^^^^^^^^^^ ^^^^^^^^^^^^
                  SHS        build date     upstream commit
```

Both tools extract the release with the pattern `SHS(\d+\.\d+\.\d+)` and report it in its own column, leaving the RPM version in place beside it.
A package whose release string carries no `SHS` marker is not part of the bundle, and its SHS column is empty.
Not every Slingshot package carries the marker.
The older Cray libfabric that `prgenv-gnu/24.7` loads is the RPM `libfabric_1.15.2.0_SSHOT2.1.3` with release `1`, from before the scheme existed, so it can be placed on the Slingshot timeline only by reading its name.
[`system-stack`][ref-tools-system-stack] reads it for the packages it tracks by name; [`user-stack`][ref-tools-user-stack] reads it for a host library it resolved, by asking which RPM owns that file, so a host-provided [libcxi][ref-pkg-libcxi] is placed on the SHS timeline from inside a uenv.

!!! tip "The commit in the release string is the upstream tag"
    On `daint` the commit in the `cray-libcxi` release string, `9d460216fdc4`, is the commit that the Spack package gives for `libcxi@13.1.0`, tagged `release/shs-13.1.0` upstream.
    The same holds for `cray-cxi-driver-devel` and `a1d91b2b0cca`.
    It does *not* hold for `cray-cassini-headers-user`, whose release string names `9acaff3b975a` while the `13.1.0` tag is `2f6e60a4`, so the correspondence is a useful hint and not a rule to rely on.

[](){#ref-shs-versions-uenv}
### In a uenv, from the Spack git version

A uenv builds these packages straight from HPE's github repositories, so Spack records a *git version* rather than a release number.
A git version is `git.<ref>`, optionally followed by `=` and the version that the reference stands for.
For the Slingshot packages the declared number is the SHS release the tag belongs to, and not a version of the package itself.

| Spack version | SHS release reported | Why |
|---|---|---|
| `git.release/shs-13.0.0=13.0.0` | `13.0.0` | A release tag, with the SHS release declared after the `=`. |
| `git.59b6de6a…=main` | unknown | An untagged commit on a branch. It names no release. |
| `13.1.0` | `13.1.0` | A plain version, already the SHS release. |

[`user-stack`][ref-tools-user-stack] normalises all three forms, and reports an untagged commit as an unknown version rather than printing the commit in a version column where it would be mistaken for one.
The commit is not lost: it stays in the install path and in the `path` field of the JSON output, and `spack-db` can be asked for the full record by dag-hash.

This is how the [cassini-headers][ref-pkg-cassini-headers], [cxi-driver][ref-pkg-cxi-driver] and [libcxi][ref-pkg-libcxi] rows of a uenv get their SHS release, so all three are placed on the same scale as the host.
The release is reported in the `shs` field and not as the component's version, because it belongs to the bundle rather than to the package: a uenv libcxi reports the soname `1.5.0` as its version and `13.0.0` as its SHS release, and both are true of the same file.

!!! warning "A tag that is absent is not a release that is absent"
    An unknown version means only that the uenv was built from an untagged commit.
    The library it produced is as real as any other, and its ABI still has to be compatible with the host driver.
    `prgenv-gnu/25.11` is built this way.

Spack renders the same version into a store directory with `=` and `/` both replaced by `_`, so `git.release/shs-13.0.0=13.0.0` becomes the directory `libcxi-git.release_shs-13.0.0_13.0.0-<hash>`.
Both spellings are recognised, but the database is the form to trust.

[](){#ref-shs-versions-comparing}
## Comparing the two sides

Once both sides report an SHS release, the comparison is direct.

!!! example "A uenv one SHS release behind its host"
    In April 2026, `prgenv-gnu/26.3` was built from SHS `13.0.0` — `cassini-headers`, `cxi-driver` and `libcxi` all report `13.0.0` — while `daint` was running an SHS `13.1.0` host.
    That difference is what a compatibility check has to reason about, and it is invisible to `ldd`, which never sees a header package at all.

The pairing that matters is the uenv's [cxi-driver][ref-pkg-cxi-driver] headers against the host's kernel driver, because that is the interface that has to agree at run time.
How `user-stack` recovers the header versions from a uenv is described in [build provenance][ref-analysis-uenv-build-provenance].
