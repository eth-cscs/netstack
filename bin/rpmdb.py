"""Read-only queries over the host RPM database.

The system half of a netstack is installed as RPMs, so the RPM database is the
source of truth for what the base image provides: the package that owns a file,
its version, and the release string that carries the Slingshot Host Software release.

Both tools use it, from opposite directions. `system-stack` asks *by package
name*, for the fixed set of components it tracks. `user-stack` asks *by path*:
runtime resolution has already found the file that actually loads, and the
question is which package put it there. The path direction is what makes a
host-provided library comparable with the same library reported by
`system-stack`.

Neither direction can be built from the other — you cannot go from name to path
without listing every file of every package — but both are asked in bulk, so
both are answered in bulk: `query_many()` and `owners()` each cover the whole
stack in a single `rpm` invocation. Spawning `rpm` per package is the one thing
that makes these tools slow, because each spawn re-opens the package database.

This module is pure standard library, and every entry point degrades to None or
an empty result when `rpm` is missing or fails, so a caller can run on a machine
that has no RPM database at all.
"""

import collections
import os
import re
import subprocess


# Standard subdirectories that sit directly under an install prefix.
_PREFIX_SUBDIRS = {'bin', 'sbin', 'lib', 'lib64', 'include', 'share', 'libexec'}

# One record per line, for the by-path query.  The fields are the four that make
# up the full package name, so that a record can always name the exact RPM it
# came from.
_QUERYFORMAT = '%{NAME}|%{VERSION}|%{RELEASE}|%{ARCH}\n'

# The by-name query additionally emits the package's file list, tagged so the
# two kinds of line can be told apart.  Asking for the files in the same
# invocation is what removes the second `rpm -ql` per package: the prefix is
# inferred from these lines instead.
_NAME_QUERYFORMAT = 'P|' + _QUERYFORMAT + '[F|%{FILENAMES}\n]'


def _rpm(args, check=True):
    """Run `rpm` with `args` and return stdout, or None if it cannot be used.

    stderr is discarded: rpm warns about its own backend ("Found NDB
    Packages.db database ...") on a healthy system, and reports a package it
    does not know there too, so a batched query simply omits what is missing.

    `check=False` keeps the output of a query that exited non-zero, which is
    what any multi-argument query does as soon as one of its arguments cannot
    be resolved — the answers for the others are still on stdout.
    """
    try:
        result = subprocess.run(['rpm'] + args, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
    except OSError:
        return None
    if check and result.returncode != 0:
        return None
    return result.stdout.decode('utf-8', 'replace')


def _rpm_raw(args):
    """Run `rpm` and return (stdout, stderr), or (None, None) if unusable.

    Only the by-path query needs stderr, and it needs it for correctness rather
    than for reporting: see `owners`.
    """
    try:
        result = subprocess.run(['rpm'] + args, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    except OSError:
        return None, None
    return (result.stdout.decode('utf-8', 'replace'),
            result.stderr.decode('utf-8', 'replace'))


# `error: file /some/path: No such file or directory` — rpm's reply for a path
# it cannot even stat, which it sends to stderr rather than stdout.
_RPM_MISSING_FILE = re.compile(r'^error: file (.+?): ')


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


def _prefix_from_files(paths):
    """Infer an install prefix from a package's file list.

    Looks for files whose path contains a standard subdirectory (bin, lib,
    include, ...) and counts how often each candidate prefix appears.  The most
    common one wins, or None if nothing can be inferred.
    """
    counts = collections.Counter()
    for line in paths:
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


def query_many(names):
    """Return {name: record} for those of `names` that are installed.

    One `rpm -q` covers every name and carries each package's file list with
    it, so the whole set costs a single process rather than two per package.
    A name rpm does not know is simply absent from the result, and each record
    carries the `prefix` inferred from its files.
    """
    names = [n for n in dict.fromkeys(names) if n]
    if not names:
        return {}
    out = _rpm(['-q', '--queryformat', _NAME_QUERYFORMAT] + names, check=False)
    if out is None:
        return {}

    found = {}
    record = None
    files = []

    def flush():
        if record is not None:
            record['prefix'] = _prefix_from_files(files)
            # Several versions of one package yield several records; keep the
            # first, as a by-name query has always done.
            found.setdefault(record['name'], record)

    for line in out.splitlines():
        if line.startswith('P|'):
            flush()
            record = _record(line[2:])
            files = []
        elif line.startswith('F|') and record is not None:
            files.append(line[2:].strip())
    flush()
    return found


def query(name):
    """Return {name, version, release, arch, package, prefix} for an RPM, or None.

    `version` and `release` are the raw strings that rpm reports; nothing is
    normalised here, because the release string has to keep the SHS marker and
    the build metadata that a caller may want to read.
    """
    return query_many([name]).get(name)


def installed(name):
    """True if the named RPM is installed."""
    return _rpm(['-q', name]) is not None


def owners(paths):
    """Return {path: record} for the paths an RPM owns.

    One `rpm -qf` call covers every path.  rpm emits its results in argument
    order, so the reply is walked alongside the input — but it answers a path it
    cannot resolve in one of two different ways, and both have to be accounted
    for or every later path is handed the wrong package:

    - a file that exists but no package owns produces `file ... is not owned by
      any package` on *stdout*, which names the path and so resyncs the walk;
    - a path that cannot be stat'd at all produces `error: file ...` on
      *stderr*, and *nothing* on stdout, so those paths have to be taken out of
      the sequence before the walk begins.

    Each record carries a `prefix`, inferred from the file list of the packages
    that came back — one further `rpm` call for all of them, so that a host
    component reports the same prefix here as it does when `system-stack` looks
    the same package up by name.

    Paths that no package owns are absent from the result, as are all of them
    when `rpm` is unavailable.
    """
    paths = [p for p in dict.fromkeys(paths) if p]
    if not paths:
        return {}
    out, err = _rpm_raw(['-qf', '--queryformat', _QUERYFORMAT] + paths)
    if out is None:
        return {}

    rejected = set()
    for line in err.splitlines():
        m = _RPM_MISSING_FILE.match(line.strip())
        if m:
            rejected.add(m.group(1))
    queue = [p for p in paths if p not in rejected]

    position = {p: i for i, p in enumerate(queue)}
    found = {}
    i = 0
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('file ') or line.startswith('error:'):
            # `file <path> is not owned by any package`: skip past that path.
            for path in queue:
                if path in line:
                    i = position[path] + 1
                    break
            continue
        record = _record(line)
        if record is None or i >= len(queue):
            continue
        # A file owned by several packages yields several lines; keep the first.
        found.setdefault(queue[i], record)
        i += 1

    prefixes = query_many([r['name'] for r in found.values()])
    for record in found.values():
        owner = prefixes.get(record['name'])
        record['prefix'] = owner['prefix'] if owner else None
    return found


def names():
    """Return the set of installed RPM names, or an empty set."""
    out = _rpm(['-qa', '--queryformat', '%{NAME}\n'])
    if out is None:
        return set()
    return {line.strip() for line in out.splitlines() if line.strip()}
