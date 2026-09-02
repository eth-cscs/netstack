[](){#ref-json-output}
# JSON output

`system-stack` and `user-stack` both accept `--format json`. This is the machine-readable form of the same report that `pretty` and `markdown` print as a table.
Every field on this page appears in the JSON, even where a table cell shows a `-` for a missing value.
This page is the schema reference. [Tools][ref-tools] describes how to run the tools themselves.

[](){#ref-json-output-components}
## Components

Both tools report their `components` field as a list of records. The records share one vocabulary, defined once in `netstack.py`. [The component record][ref-tools-components] describes it in full.

| Field | What it holds |
|---|---|
| `name` | The component name, from the same vocabulary on both sides: the [package pages][ref-pkg]. |
| `version` | The component's own version, in whatever scheme its provider names it. |
| `version_source` | Where that number was read: `rpm`, `store`, `path`, `soname`, `spack` or `runtime`. |
| `shs` | The [SHS release][ref-shs] the component belongs to, or `null`. |
| `origin` | What supplied the component, or `null` when it is not present. |
| `prefix` | The install prefix, or `null`. |
| `path` | The file that was resolved, for a component found by runtime resolution. |
| `via` | How the dynamic loader found it. |

`origin` takes one of four shapes. It holds the evidence specific to what supplied the component, not anything already reported at the top level.

### `origin.type: "uenv"`

A package the uenv built, identified by its Spack dag-hash.

```json title="libfabric, built by the uenv in prgenv-gnu/25.11:v1"
{
  "name": "libfabric",
  "version": "2.3.1",
  "version_source": "store",
  "shs": null,
  "origin": {
    "type": "uenv",
    "mount": "/user-environment",
    "hash": "ekke44pxlz6r3xg5o4h2b7c1v9wq0djk",
    "spack_version": "2.3.1"
  },
  "prefix": null,
  "path": "/user-environment/env/default/lib/libfabric.so.1.29.1",
  "via": "rpath"
}
```

`origin.hash` is the full 32-character Spack dag-hash.
The pretty and markdown tables show only its first seven characters, to save width. So `ekke44pxlz6r3xg5o4h2b7c1v9wq0djk` above is the same package that the [Tools][ref-tools-user-stack] example table shows truncated as `ekke44p`.

### `origin.type: "rpm"`

A package in the host image, identified by its full RPM name.

```json title="A host-provided libcxi, reported identically by both tools"
{
  "name": "libcxi",
  "version": "1.0.2",
  "version_source": "rpm",
  "shs": "13.1.0",
  "origin": {
    "type": "rpm",
    "package": "cray-libcxi-1.0.2-SHS13.1.0_20260127170946_9d460216fdc4.aarch64",
    "name": "cray-libcxi",
    "version": "1.0.2",
    "release": "SHS13.1.0_20260127170946_9d460216fdc4"
  },
  "prefix": "/usr",
  "path": null,
  "via": null
}
```

`version` at the top level is the plain release trimmed out of `origin.version`. See [`rpm_version`][ref-shs] for a case where the two differ, such as `libfabric`'s older `1.15.2.0_SSHOT2.1.3`.

### `origin.type: "host"`

A file on the host that no RPM owns.

```json title="The Cray libfabric that prgenv-gnu/25.6 loads, owned by no RPM"
{
  "name": "libfabric",
  "version": "1.22.0",
  "version_source": "path",
  "shs": null,
  "origin": {
    "type": "host"
  },
  "prefix": null,
  "path": "/opt/cray/libfabric/1.22.0/lib64/libfabric.so.1",
  "via": "rpath"
}
```

`/opt/cray/libfabric/1.22.0` is the canonical example. `rpm -qf` against anything under that tree returns nothing, so `origin` carries nothing beyond its `type`.
See [the RPMs behind the system copies][ref-pkg-libfabric] for how the tools confirmed this.

### No origin

A component the tools looked for but did not find keeps its row, with `origin` set to `null`.
`system-stack` includes such rows, because a missing package that the system expects is itself a diagnosis. `user-stack` omits them entirely.

```json title="A tracked package that is not installed, from system-stack"
{
  "name": "vast",
  "version": null,
  "version_source": null,
  "shs": null,
  "origin": null,
  "prefix": null,
  "path": null,
  "via": null
}
```

[](){#ref-json-output-system-stack}
## system-stack

```json title="The shape of `system-stack --format json`"
{
  "properties": [ { "key": "...", "value": "..." } ],
  "components": [ { "name": "...", "...": "..." } ],
  "gcc": [ { "major": 0, "version": "...", "...": "..." } ]
}
```

`components` is the list described in [Components][ref-json-output-components] above.

`properties` is a flat list of `{"key": str, "value": str}` pairs that describe the system itself, not a component. Examples are the OS, the cluster name, and the NVIDIA driver and CUDA versions where a GPU is present.

```json title="One entry of properties"
{ "key": "cluster", "value": "daint" }
```

`gcc` is a list of every installed GCC major version, one entry per version:

```json title="One entry of gcc"
{
  "major": 12,
  "version": "12.3.0",
  "prefix": "/usr",
  "c": "/usr/bin/gcc-12",
  "cxx": "/usr/bin/g++-12",
  "fortran": null
}
```

`c`, `cxx` and `fortran` are the path to that language's compiler driver, or `null` when the matching package (`gcc{N}-c++`, `gcc{N}-fortran`) is not installed.
A GCC major version with `c: null` means the base `gcc{N}` package itself is missing.

[](){#ref-json-output-user-stack}
## user-stack

```json title="The shape of `user-stack --format json`"
{
  "uenv": { "label": "...", "...": "..." },
  "fabric_providers": [ "..." ],
  "components": [ { "name": "...", "...": "..." } ],
  "envvars": [ { "name": "...", "value": "...", "component": "..." } ]
}
```

`components` is the list described in [Components][ref-json-output-components] above.

`uenv` identifies the loaded uenv:

```json title="uenv identity, for prgenv-gnu/25.11:v1"
{
  "label": "prgenv-gnu/25.11:v1",
  "name": "prgenv-gnu/25.11",
  "mount": "/user-environment",
  "view": "default",
  "arch": "linux-sles15-neoverse_v2",
  "system": "daint"
}
```

`fabric_providers` is the list of libfabric providers `fi_info -l` reports, for example the [providers compiled into libfabric][ref-pkg-libfabric] on a Grace-Hopper node:

```json title="fabric_providers on a Grace-Hopper node"
["cxi", "ofi_rxm", "udp", "tcp", "sockets"]
```

`envvars` is the list of netstack-relevant [environment variables][ref-envvars] that are currently set. Each entry pairs a variable with the component it affects:

```json title="One entry of envvars"
{ "name": "FI_MR_CACHE_MONITOR", "value": "kdreg2", "component": "libfabric" }
```

Without a loaded uenv view, `user-stack --format json` prints a single error object instead of this envelope:

```json title="user-stack --format json outside a uenv"
{ "error": "no uenv view is loaded" }
```
