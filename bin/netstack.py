"""The shared vocabulary of a netstack component.

`system-stack` and `user-stack` report the two halves of one stack, and a
library such as `libcxi` can appear in either half — or, when a uenv ships its
own copy, in both at once.  They therefore describe a component with one
record, defined here, so that the two reports can be compared field by field:

    name            logical component name, the same on both sides
    version         the component's own version, as its provider names it
    version_source  how that number was obtained: rpm, store, path, soname,
                    spack, runtime
    shs             the Slingshot Host Software release it belongs to
    origin          what supplied it, or None when it is not present
    prefix          install prefix
    path            the resolved file, when there is one
    via             how the loader found it, for a runtime-resolved component

The split between `version` and `shs` matters.  A component's own version is
whatever its provider calls it, and the same library is `1.0.2` to RPM and
`1.5.0` to its soname.  The SHS release is the one number both halves of the
stack have in common, and it is the axis a compatibility check reasons along,
so it is a field of its own rather than a version in disguise.

`origin` holds the evidence specific to the kind of provider, and only what is
not already at the top level: a dag-hash and the raw Spack version for a uenv
package, an RPM name and release string for an RPM.

Besides the record, this module owns what both tools do with it: running an
external probe (`run`), rendering a table of rows against a column spec
(`Column`, `print_table`), and the `--format` flag itself.  A tool therefore
declares *what* it collects and *which* columns it can fill, and never how a
table is drawn — that is why the two reports look alike.

`rich` and `tabulate` are imported inside the rendering functions, so importing
this module costs nothing beyond the standard library and `--format json` never
pays for a table renderer it does not use.
"""

import os
import re
import subprocess


# ---------------------------------------------------------------------------
# the record
# ---------------------------------------------------------------------------

# The ways a version can be established, in the order a reader meets them.
VERSION_SOURCES = ('rpm', 'store', 'path', 'soname', 'spack', 'runtime')


def component(name, version=None, version_source=None, shs=None, origin=None,
              prefix=None, path=None, via=None):
    """Build a component record.

    Every field is optional but always present, so consumers never have to
    distinguish "absent key" from "unknown value".
    """
    return {
        'name': name,
        'version': version,
        'version_source': version_source,
        'shs': shs,
        'origin': origin,
        'prefix': prefix,
        'path': path,
        'via': via,
    }


def origin_uenv(mount=None, hash=None, spack_version=None):
    """Origin of a component supplied by a uenv (a Spack install tree).

    `spack_version` is the version string exactly as the database records it,
    kept because it can be a git version whose meaning (a commit, or the SHS
    release a tag belongs to) does not survive into `version`.
    """
    return {'type': 'uenv', 'mount': mount, 'hash': hash,
            'spack_version': spack_version}


def origin_rpm(record):
    """Origin of a component supplied by an RPM, from an `rpmdb` record.

    `package` is the full package name, `name-version-release.arch`, which
    identifies the exact build; `version` is the raw version string it carries,
    kept because the top-level `version` is the plain release trimmed out of it.
    """
    return {'type': 'rpm', 'package': record.get('package'),
            'name': record.get('name'), 'version': record.get('version'),
            'release': record.get('release')}


def origin_host():
    """Origin of a system file that no package owns.

    `/opt/cray/libfabric/1.22.0` is one: it is on the host, it is what loads,
    and the RPM database knows nothing about it.
    """
    return {'type': 'host'}


def origin_type(row):
    """The origin type of a row: 'uenv', 'rpm', 'host', or None if absent."""
    origin = row.get('origin')
    return origin.get('type') if origin else None


def rpm_fields(record):
    """The component fields an `rpmdb` record establishes.

    Both tools meet the same RPM from opposite directions — `system-stack` by
    package name, `user-stack` by the path of a host library that loaded — and
    a component reported from an RPM has to look the same either way.  That is
    the whole point of the shared record, so the mapping lives here rather than
    once in each tool.
    """
    version = rpm_version(record.get('version'))
    return {
        'version': version,
        'version_source': 'rpm' if version else None,
        'shs': shs_from_release(record.get('release')),
        'origin': origin_rpm(record),
        'prefix': record.get('prefix'),
    }


def from_rpm(name, record, **extra):
    """A complete component record for an RPM-provided component."""
    row = component(name, **extra)
    row.update(rpm_fields(record))
    return row


def path_under(path, root):
    """True if `path` is `root` or lives beneath it.

    Both arguments are expected to be resolved already: this is called once per
    component per mount, and resolving a constant mount point over and over is
    the kind of waste that adds up on a squashfs.
    """
    if not path or not root:
        return False
    root = root.rstrip(os.sep)
    return path == root or path.startswith(root + os.sep)


# ---------------------------------------------------------------------------
# running external probes
# ---------------------------------------------------------------------------

def run(argv, check=True):
    """Run `argv` and return its stdout, or None if it cannot be used.

    Every fact these tools report about a live system comes from some external
    command — rpm, libtree, ldd, nvidia-smi, fi_info — and every one of them
    may be missing, so the "absent tool is not an error" policy is written once
    here rather than at each probe.

    stderr is discarded: a probe that failed says so through its return code,
    and several of these commands chatter on stderr when healthy (rpm warns
    about its own backend).

    `check=False` keeps the output of a command that exited non-zero, which is
    what a multi-argument `rpm -qf` needs — the answers for the paths it could
    resolve are still on stdout.
    """
    try:
        result = subprocess.run(argv, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
    except OSError:
        return None
    if check and result.returncode != 0:
        return None
    return result.stdout.decode('utf-8', 'replace')


def run_lines(argv, check=True):
    """`run`, split into lines; an unusable command yields no lines."""
    out = run(argv, check=check)
    return out.splitlines() if out is not None else []


_NVIDIA_DRIVER = re.compile(r'DRIVER version\s*:\s*([\d.]+)', re.IGNORECASE)
_NVIDIA_CUDA = re.compile(r'CUDA Version\s*:\s*([\d.]+)', re.IGNORECASE)


def nvidia_versions():
    """Return (driver, cuda) as `nvidia-smi --version` reports them.

    Both tools ask this of the same machine, and a stack is compared across the
    two halves, so they have to read it the same way: one parser, one answer.
    """
    out = run(['nvidia-smi', '--version'])
    if out is None:
        return None, None
    driver = _NVIDIA_DRIVER.search(out)
    cuda = _NVIDIA_CUDA.search(out)
    return (driver.group(1) if driver else None,
            cuda.group(1) if cuda else None)


# ---------------------------------------------------------------------------
# SHS release detection
# ---------------------------------------------------------------------------

# Components whose Spack version *is* an SHS release.  The Spack packages for
# these three are versioned by the release bundle they belong to rather than by
# the upstream version of the component, whether they name a tag
# (`git.release/shs-13.0.0=13.0.0`) or a plain number (`13.1.0`).  libfabric is
# deliberately not in the set: a uenv builds it from an upstream OFI release, so
# its version is its own and only a host RPM can place it on the SHS timeline.
SHS_COMPONENTS = ('libcxi', 'cassini-headers', 'cxi-driver')

# An RPM release string carries the release it was built for, alongside a build
# timestamp and a commit: SHS13.1.0_20260127170946_9d460216fdc4.
_SHS_RELEASE = re.compile(r'SHS(\d+\.\d+\.\d+)')

# A Spack git version is `git.<ref>`, with the version the reference stands for
# declared after an `=`.  For the Slingshot packages, built from HPE's github
# repositories, that number is the SHS release the tag belongs to:
#
#   git.release/shs-13.0.0=13.0.0  ->  SHS 13.0.0
#   git.59b6de6a…=main             ->  nothing: an untagged commit on a branch
#
# Older uenvs pin an untagged commit rather than a release tag, and a commit on
# its own says nothing about which release it belongs to.
_GIT_COMMIT = re.compile(r'[0-9a-f]{7,40}')
_NUMERIC_VERSION = re.compile(r'\d[\w.]*')


def rpm_version(version):
    """The plain release named by an RPM version string.

    An RPM version can carry vendor packaging on its tail, fused to the last
    component: `lustre-client` is `2.15.7.2_cray_39_g654b360` and the Cray
    libfabric of `prgenv-gnu/24.7` is `1.15.2.0_SSHOT2.1.3`.  Only the leading
    run of purely numeric components is the release, so those become `2.15.7`
    and `1.15.2`.  Nothing is lost: the raw string stays in the `rpm` origin,
    which also names the package it belongs to.
    """
    if not version:
        return None
    parts = []
    for part in version.split('.'):
        if not part.isdigit():
            break
        parts.append(part)
    return '.'.join(parts) if parts else version


def shs_from_release(release):
    """SHS release named by an RPM release string, or None."""
    if not release:
        return None
    m = _SHS_RELEASE.search(release)
    return m.group(1) if m else None


def parse_git_version(version):
    """Return (is_git, declared) for a Spack version string.

    `is_git` says whether this is a git version, which is never a version of
    the package itself.  `declared` is the version the reference stands for, or
    None for a bare commit or a branch such as `main`.

    Both the database form and the store-directory rendering of it are
    accepted, the latter having had `=` and `/` replaced by `_`:

        git.release/shs-13.0.0=13.0.0  (database)
        git.release_shs-13.0.0_13.0.0  (store directory)
    """
    if not version or not version.startswith('git.'):
        return False, None
    rest = version[len('git.'):]
    ref, sep, declared = rest.partition('=')
    if not sep:
        ref, sep, declared = rest.rpartition('_')
    if not sep or _GIT_COMMIT.fullmatch(ref):
        return True, None
    return True, declared if _NUMERIC_VERSION.fullmatch(declared) else None


def is_release_version(version):
    """True if `version` is a version of the package rather than a git ref.

    A git version names a commit or a tag.  What release that tag belongs to is
    reported as `shs`, so a git version must never be handed back as a version.
    """
    return bool(version) and not parse_git_version(version)[0]


def shs_from_spack_version(name, version):
    """SHS release a uenv package was built from, or None.

    Only an `SHS_COMPONENTS` package can name one.  Its version is the release
    either directly, or through the tag that a git version points at; an
    untagged commit names no release at all.
    """
    if name not in SHS_COMPONENTS or not version:
        return None
    is_git, declared = parse_git_version(version)
    if is_git:
        return declared
    return version if _NUMERIC_VERSION.fullmatch(version) else None


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

class Column:
    """One column of a report table.

    `cell` reads the value out of a row, `style_of` optionally picks a per-row
    colour for it, and `absent` is what the pretty renderer shows in place of a
    missing value.  Both renderers walk the same list, which is what keeps the
    pretty, markdown and JSON views of a table from drifting apart.
    """

    __slots__ = ('key', 'header', 'style', 'cell', 'no_wrap', 'justify',
                 'style_of', 'absent')

    def __init__(self, key, header, style=None, cell=None, no_wrap=True,
                 justify=None, style_of=None, absent='-'):
        self.key = key
        self.header = header
        self.style = style
        self.cell = cell if cell is not None else (lambda row: row.get(key))
        self.no_wrap = no_wrap
        self.justify = justify
        self.style_of = style_of
        self.absent = absent


def table(title=None, show_header=True):
    """A `rich` table in the house style.

    Every table these tools print is built here, so the look of a report is
    decided in one place.
    """
    from rich import box
    from rich.style import Style
    from rich.table import Table
    return Table(box=box.ROUNDED, title=title, show_header=show_header,
                 header_style=Style(color='bright_white', bold=True),
                 border_style=Style(color='grey50'))


def print_table(rows, columns, fmt, title=None, show_header=True):
    """Print `rows` against a list of `Column`s, in `fmt`."""
    if fmt == 'markdown':
        _print_table_markdown(rows, columns)
    else:
        _print_table_pretty(rows, columns, title, show_header)


def _print_table_pretty(rows, columns, title=None, show_header=True):
    from rich.console import Console
    tbl = table(title=title, show_header=show_header)
    for col in columns:
        tbl.add_column(col.header, style=col.style, no_wrap=col.no_wrap,
                       justify=col.justify or 'left')
    for row in rows:
        cells = []
        for col in columns:
            value = col.cell(row)
            if value is None or value == '':
                cells.append('[dim]{}[/dim]'.format(col.absent))
                continue
            style = col.style_of(row) if col.style_of else None
            cells.append('[{0}]{1}[/{0}]'.format(style, value) if style
                         else str(value))
        tbl.add_row(*cells)
    Console().print(tbl)


def _print_table_markdown(rows, columns):
    from tabulate import tabulate
    headers = [col.header for col in columns]
    body = [[col.cell(row) if col.cell(row) not in (None, '') else '-'
             for col in columns] for row in rows]
    print(tabulate(body, headers=headers, tablefmt='github'))


def print_properties(pairs, fmt, key_header='Key', value_header='Value',
                     value_style='bright_green'):
    """Print an ordered list of (key, value) pairs; empty values are dropped.

    Both tools open their report with a block of this shape — the system
    properties on one side, the uenv identity on the other.
    """
    rows = [{'key': k, 'value': v} for k, v in pairs if v]
    columns = [Column('key', key_header, style='bold cyan'),
               Column('value', value_header, style=value_style, no_wrap=False)]
    print_table(rows, columns, fmt, show_header=False)


# ---------------------------------------------------------------------------
# the component table
# ---------------------------------------------------------------------------

_ORIGIN_STYLE = {'uenv': 'bright_green', 'rpm': 'bright_yellow',
                 'host': 'bright_yellow'}

# A row with no origin was looked for and not found.  `system-stack` reports
# those (that Lustre is missing is itself a diagnosis); `user-stack` omits them.
_ABSENT = 'not installed'


def _hash(row):
    origin = row.get('origin') or {}
    return (origin.get('hash') or '')[:7] or None


# Found via is the one column allowed to wrap, so that a narrow terminal folds
# the free text ("built into libcxi, libfabric") rather than squeezing a version
# or a hash down to nothing.
COMPONENT_COLUMNS = {
    'name':    Column('name', 'Component', style='bold cyan'),
    'version': Column('version', 'Version', style='bright_green'),
    'shs':     Column('shs', 'SHS', style='bright_yellow'),
    'origin':  Column('origin', 'Origin',
                      cell=lambda row: origin_type(row) or _ABSENT,
                      style_of=lambda row: _ORIGIN_STYLE.get(origin_type(row),
                                                             'dim')),
    'via':     Column('via', 'Found via', style='blue', no_wrap=False),
    'hash':    Column('hash', 'Hash', style='blue', cell=_hash),
    'prefix':  Column('prefix', 'Prefix', style='bright_magenta'),
}


def print_components(rows, keys, fmt):
    """Print a component table, showing the columns named by `keys`."""
    print_table(rows, [COMPONENT_COLUMNS[k] for k in keys], fmt)


# ---------------------------------------------------------------------------
# the command line
# ---------------------------------------------------------------------------

def add_format_argument(parser, formats=('pretty', 'markdown', 'json')):
    """Add the `--format` flag both stack tools share."""
    parser.add_argument('--format', choices=list(formats), default='pretty',
                        help='Output format (default: pretty)')
    return parser


def print_json(obj):
    import json
    print(json.dumps(obj, indent=2))
