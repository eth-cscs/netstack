[](){#ref-shs}
# Slingshot Host Software (SHS)

HPE Slingshot Host Software is the software that HPE ships for the Slingshot interconnect of an HPE Cray EX system.
SHS is a *release bundle*, not a single package. One SHS version, for example `13.1.0`, names a kernel driver, a set of user-space libraries and a set of headers. HPE builds, tests and releases these together.

You diagnose fabric problems by comparing SHS versions. SHS is the only number that both halves of the [system/user split][ref-index-user] share.
The versions of `cxi-driver`, `cassini-headers` and `libcxi` in a software stack must belong to the same SHS release. HPE tests and packages them this way.
If a user software stack provides one or more of these packages, you must check that they are compatible with the system SHS installation.

!!! note "This page is a working set of notes"
    This page records what we know about SHS. We update it as the tooling grows. We do not write it once and leave it unchanged.
    We observed everything below on `daint`, and we give a date where it matters.

[](){#ref-shs-contents}
## What is in SHS

The netstack tools track two parts of SHS: the Slingshot NIC driver, and the user-space stack that talks to it.
Each one exists twice: as an RPM in the host OS image, and as a Spack package that a uenv can build for itself.

| Component | Host RPM | Spack package | Upstream repository |
|---|---|---|---|
| [cxi-driver][ref-pkg-cxi-driver] | `cray-cxi-driver-devel` | `cxi-driver` | [shs-cxi-driver](https://github.com/HewlettPackard/shs-cxi-driver) |
| [cassini-headers][ref-pkg-cassini-headers] | `cray-cassini-headers-user` | `cassini-headers` | [shs-cassini-headers](https://github.com/HewlettPackard/shs-cassini-headers) |
| [libcxi][ref-pkg-libcxi] | `cray-libcxi` | `libcxi` | [shs-libcxi](https://github.com/HewlettPackard/shs-libcxi) |
| [libfabric][ref-pkg-libfabric] | `libfabric` | `libfabric` | upstream OFI, with the HPE `cxi` provider |

Not everything in the netstack comes from SHS.
[xpmem][ref-pkg-xpmem], Slurm and Lustre are host software with their own release cycles. [`system-stack`][ref-tools-system-stack] reports no SHS release for them.

This is what `daint`, an SHS 13.1.0 host, had installed in September 2026:

| Component | RPM version | SHS | Prefix |
|---|---|---|---|
| cassini-headers | 1.1.2 | 13.1.0 | `/usr` |
| libcxi | 1.0.2 | 13.1.0 | `/usr` |
| cxi-driver | 1.0.0 | 13.1.0 | `/usr` |
| libfabric | 2.3.1 | 13.1.0 | `/opt/cray/libfabric/2.3.1` |

The RPM version and the SHS release are different numbers. You cannot derive one from the other.
`cray-libcxi` is at `1.0.2` inside SHS `13.1.0`. The soname of the same library is a third number, `1.5.0`.
See [version namespaces][ref-analysis-uenv-version-namespaces] for the full list of numbers that describe one library.

[](){#ref-shs-versions}
## How to detect the SHS version

[](){#ref-shs-versions-host}
### On the host, from the RPM release string

The SHS release is not the RPM version. It appears in the RPM *release* field, together with a build timestamp and a short commit:

```
cray-libcxi-1.0.2-SHS13.1.0_20260127170946_9d460216fdc4
                  ^^^^^^^^^ ^^^^^^^^^^^^^^ ^^^^^^^^^^^^
                  SHS        build date     upstream commit
```

Both tools extract the release with the pattern `SHS(\d+\.\d+\.\d+)` and report it in its own `shs` field. They leave the RPM version in place, beside it, in `origin.version`.
A package whose release string carries no `SHS` marker is not part of the bundle. Its `shs` field is `null`.
Not every Slingshot package carries the marker.
The older Cray libfabric that `prgenv-gnu/24.7` loads is the RPM `libfabric_1.15.2.0_SSHOT2.1.3`, with release `1`. This RPM predates the SHS release-string scheme. You can place it on the Slingshot timeline only if you read its name. The `rpm` origin records the name in full.
[`system-stack`][ref-tools-system-stack] tracks packages by name, and reads the RPM name to place them on the timeline. [`user-stack`][ref-tools-user-stack] resolves a host library to a file, then asks which RPM owns that file, and reads the RPM name the same way. This places a host-provided [libcxi][ref-pkg-libcxi] on the SHS timeline, from inside a uenv.

!!! tip "The commit in the release string is the upstream tag"
    On `daint`, the commit in the `cray-libcxi` release string is `9d460216fdc4`. This is the same commit that the Spack package gives for `libcxi@13.1.0`. Upstream, HPE tags this commit `release/shs-13.1.0`.
    The same holds for `cray-cxi-driver-devel` and `a1d91b2b0cca`.
    It does *not* hold for `cray-cassini-headers-user`. Its release string names `9acaff3b975a`, while the `13.1.0` tag is `2f6e60a4`. So the correspondence is a useful hint, not a rule you can rely on.

[](){#ref-shs-versions-uenv}
### In a uenv, from the Spack git version

A uenv builds these packages straight from HPE's github repositories, so Spack records a *git version* rather than a release number.
A git version has the form `git.<ref>`. It can optionally continue with `=` and then the version that the reference stands for.
For the Slingshot packages, the declared number is the SHS release that the tag belongs to, not a version of the package itself.

| Spack version | SHS release reported | Why |
|---|---|---|
| `git.release/shs-13.0.0=13.0.0` | `13.0.0` | A release tag, with the SHS release after the `=`. |
| `git.59b6de6a…=main` | unknown | An untagged commit on a branch. It names no release. |
| `13.1.0` | `13.1.0` | A plain version, already the SHS release. |

[`user-stack`][ref-tools-user-stack] normalises all three forms. It reports an untagged commit as an unknown version. It does not report the commit itself as the `version`, because that would be mistaken for a real version.
The commit is not lost. It stays in the install path and in the `path` field of the JSON output. You can ask `spack-db` for the full record by dag-hash.

This is how the [cassini-headers][ref-pkg-cassini-headers], [cxi-driver][ref-pkg-cxi-driver] and [libcxi][ref-pkg-libcxi] rows of a uenv get their SHS release. You can then compare all three to the system SHS installation.
`user-stack` reports the release in the `shs` field, not as the component's version, because the release belongs to the bundle, not the package. For example, a uenv's libcxi reports the soname `1.5.0` as its version and `13.0.0` as its SHS release. Both are true of the same file.

!!! warning "A tag that is absent is not a release that is absent"
    An unknown version for a package in a uenv means the package came from an untagged commit.
    Older versions of the `cassini-headers`, `lib-cxi` and other Spack packages referred directly to commit SHAs on the `main` branch. So we cannot associate these commits with specific versions.
    The `prgenv-gnu/25.11` uenv follows this pattern.

Spack renders the same version into a store directory. It replaces both `=` and `/` with `_`. So `git.release/shs-13.0.0=13.0.0` becomes the directory `libcxi-git.release_shs-13.0.0_13.0.0-<hash>`.
The tools recognise both spellings. Trust the database form.

[](){#ref-shs-versions-comparing}
## How to compare the two sides

Once both sides report an SHS release, the comparison is direct.

!!! example "A uenv one SHS release behind its host"
    In April 2026, `prgenv-gnu/26.3` came from SHS `13.0.0`: `cassini-headers`, `cxi-driver` and `libcxi` all report `13.0.0`. At the same time, `daint` ran an SHS `13.1.0` host.
    A compatibility check must find that difference. It is invisible to `ldd`. `ldd` never sees a header package at all.

The pairing that matters is the uenv's [cxi-driver][ref-pkg-cxi-driver] headers against the host's kernel driver. This is the interface that must agree at run time.
[Build provenance][ref-analysis-uenv-build-provenance] describes how `user-stack` recovers the header versions from a uenv.
