"""The shared vocabulary of a netstack component.

`system-stack` and `user-stack` report the two halves of one stack, and a
library such as `libcxi` can appear in either half — or, when a uenv ships its
own copy, in both at once.  They therefore describe a component with one
record, defined here, so that the two reports can be compared field by field:

    name            logical component name, the same on both sides
    version         the component's own version, as its provider names it
    version_source  how that number was obtained: rpm, store, path, soname,
                    runtime
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

This module is imported by both tools, which declare `rich` and `tabulate`.
"""

import re

from rich import box
from rich.console import Console
from rich.style import Style
from rich.table import Table
from tabulate import tabulate


# ---------------------------------------------------------------------------
# the record
# ---------------------------------------------------------------------------

def component(name, version=None, version_source=None, shs=None, origin=None,
              prefix=None, path=None, via=None):
    """Build a component record.

    Every field is optional but always present, so consumers never have to
    distinguish "absent key" from "unknown value".
    """
    return {
        'name': name,
        'version': version,
        'version_source': version_source if version else None,
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
    """Origin of a component supplied by an RPM, from an `rpmdb` record."""
    return {'type': 'rpm', 'name': record.get('name'),
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

_ORIGIN_STYLE = {'uenv': 'bright_green', 'rpm': 'bright_yellow',
                 'host': 'bright_yellow'}

# A row with no origin was looked for and not found.  `system-stack` reports
# those (that Lustre is missing is itself a diagnosis); `user-stack` omits them.
_ABSENT = 'not installed'


def _hash(row):
    origin = row.get('origin') or {}
    return (origin.get('hash') or '')[:7] or None


def _origin_cell(row):
    return origin_type(row) or _ABSENT


# key -> (header, style, cell, no_wrap).  Found via is the one column allowed to
# wrap, so that a narrow terminal folds the free text ("built into libcxi,
# libfabric") rather than squeezing a version or a hash down to nothing.
_COLUMNS = {
    'name':    ('Component', 'bold cyan',      lambda r: r['name'],    True),
    'version': ('Version',   'bright_green',   lambda r: r['version'], True),
    'shs':     ('SHS',       'bright_yellow',  lambda r: r['shs'],     True),
    'origin':  ('Origin',    None,             _origin_cell,           True),
    'via':     ('Found via', 'blue',           lambda r: r['via'],     False),
    'hash':    ('Hash',      'blue',           _hash,                  True),
    'prefix':  ('Prefix',    'bright_magenta', lambda r: r['prefix'],  True),
}


def print_components_pretty(rows, columns):
    """Print a component table for the terminal."""
    table = Table(box=box.ROUNDED,
                  header_style=Style(color='bright_white', bold=True),
                  border_style=Style(color='grey50'))
    for key in columns:
        header, style, _, no_wrap = _COLUMNS[key]
        table.add_column(header, style=style, no_wrap=no_wrap)

    for row in rows:
        cells = []
        for key in columns:
            value = _COLUMNS[key][2](row)
            if value is None:
                cells.append('[dim]-[/dim]')
            elif key == 'origin':
                style = _ORIGIN_STYLE.get(origin_type(row), 'dim')
                cells.append('[{0}]{1}[/{0}]'.format(style, value))
            else:
                cells.append(str(value))
        table.add_row(*cells)

    Console().print(table)


def print_components_markdown(rows, columns):
    """Print a component table as a GitHub-flavoured markdown table."""
    headers = [_COLUMNS[key][0] for key in columns]
    table = [[_COLUMNS[key][2](row) or '-' for key in columns] for row in rows]
    print(tabulate(table, headers=headers, tablefmt='github'))
