"""Read-only queries over the host RPM database.

The system half of a netstack is installed as RPMs, so the RPM database is the
source of truth for what the base image provides: the package that owns a file,
its version, and the release string that carries the Slingshot Host Software release.

Both tools use it, from opposite directions. `system-stack` asks *by package
name*, for the fixed set of components it tracks. `user-stack` asks *by path*:
runtime resolution has already found the file that actually loads, and the
question is which package put it there. The path direction is what makes a
host-provided library comparable with the same library reported by
`system-stack`, and `owners()` answers it for every path in one call.

This module is pure standard library, and every entry point degrades to None or
an empty result when `rpm` is missing or fails, so a caller can run on a machine
that has no RPM database at all.
"""

import collections
import os
import subprocess


# Standard subdirectories that sit directly under an install prefix.
_PREFIX_SUBDIRS = {'bin', 'sbin', 'lib', 'lib64', 'include', 'share', 'libexec'}

# One record per line, for both the by-name and the by-path queries.  The
# fields are the four that make up the full package name, so that a record can
# always name the exact RPM it came from.
_QUERYFORMAT = '%{NAME}|%{VERSION}|%{RELEASE}|%{ARCH}\n'


def _rpm(args, check=True):
    """Run `rpm` with `args` and return stdout, or None if it cannot be used.

    stderr is discarded: rpm warns about its own backend ("Found NDB
    Packages.db database ...") on a healthy system, and a failed query is
    reported through the return code.

    `check=False` keeps the output of a query that exited non-zero, which is
    what a multi-path `rpm -qf` does as soon as one of its paths is owned by no
    package — the answers for the other paths are still on stdout.
    """
    try:
        result = subprocess.run(['rpm'] + args, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
    except OSError:
        return None
    if check and result.returncode != 0:
        return None
    return result.stdout.decode('utf-8', 'replace')


def _record(line):
    """Parse one `_QUERYFORMAT` line into a dict, or None.

    `package` is the full package name, `name-version-release.arch`, exactly as
    `rpm -q` prints it, so a record can be handed back to rpm unchanged.
    """
    parts = line.split('|')
    if len(parts) != 4:
        return None
    name, version, release, arch = (p.strip() for p in parts)
    if not name:
        return None
    package = name
    if version and release:
        package = '{}-{}-{}'.format(name, version, release)
        if arch:
            package = '{}.{}'.format(package, arch)
    return {'name': name, 'version': version or None, 'release': release or None,
            'arch': arch or None, 'package': package}


def installed(name):
    """True if the named RPM is installed."""
    return _rpm(['-q', name]) is not None


def query(name):
    """Return {name, version, release, arch, package, prefix} for an RPM, or None.

    `version` and `release` are the raw strings that rpm reports; nothing is
    normalised here, because the release string has to keep the SHS marker and
    the build metadata that a caller may want to read.
    """
    out = _rpm(['-q', '--queryformat', _QUERYFORMAT, name])
    if out is None:
        return None
    for line in out.splitlines():
        record = _record(line)
        if record:
            record['prefix'] = infer_prefix(name)
            return record
    return None


def owners(paths):
    """Return {path: record} for the paths an RPM owns.

    One `rpm -qf` call covers every path.  rpm emits its results in argument
    order and reports a path no package owns as a `file ... is not owned by any
    package` line on *stdout*, so the reply can be walked alongside the input:
    a not-owned line names the path it refers to and resyncs the position, and
    every other line belongs to the path currently under the cursor.

    Paths that no package owns are absent from the result, as are all of them
    when `rpm` is unavailable.
    """
    paths = [p for p in dict.fromkeys(paths) if p]
    if not paths:
        return {}
    out = _rpm(['-qf', '--queryformat', _QUERYFORMAT] + paths, check=False)
    if out is None:
        return {}

    position = {p: i for i, p in enumerate(paths)}
    found = {}
    i = 0
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('file ') or line.startswith('error:'):
            # `file <path> is not owned by any package`: skip past that path.
            for path in paths:
                if path in line:
                    i = position[path] + 1
                    break
            continue
        record = _record(line)
        if record is None or i >= len(paths):
            continue
        # A file owned by several packages yields several lines; keep the first.
        found.setdefault(paths[i], record)
        i += 1
    return found


def infer_prefix(name):
    """Return the install prefix of an RPM, inferred from its file list.

    Looks for files whose path contains a standard subdirectory (bin, lib,
    include, ...) and counts how often each candidate prefix appears.  The most
    common one is returned, or None if nothing can be inferred.
    """
    out = _rpm(['-ql', name])
    if out is None:
        return None

    counts = collections.Counter()
    for line in out.splitlines():
        parts = line.split(os.sep)
        # parts[0] is '' for absolute paths; search from index 1 onwards
        for i, part in enumerate(parts[1:], start=1):
            if part in _PREFIX_SUBDIRS:
                prefix = os.sep + os.path.join(*parts[1:i]) if i > 1 else os.sep
                counts[prefix] += 1
                break

    if not counts:
        return None

    return counts.most_common(1)[0][0]


def names():
    """Return the set of installed RPM names, or an empty set."""
    out = _rpm(['-qa', '--queryformat', '%{NAME}\n'])
    if out is None:
        return set()
    return {line.strip() for line in out.splitlines() if line.strip()}
