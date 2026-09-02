"""Read-only queries over a Spack database.

Works on any Spack install tree rooted at a given ``mount`` directory — most
commonly a uenv mounted at ``/user-environment``, but nothing here is
uenv-specific. Spack records every installed package in
``<mount>/.spack-db/index.json``, which is therefore the **source of truth** for

- exact package name / version / hash,
- the install prefix of each package,
- the dependency edges between packages, tagged `build` / `link` / `run`.

`ldd` / `libtree` tell us which shared objects actually load; this database
tells us what those objects *are* and how they depend on each other — including
build-only dependencies (e.g. `cassini-headers`) that never appear in a runtime
dependency tree.

Like `rpmdb`, this module degrades rather than raising: `SpackDB.open` returns
None when there is no readable database, so a caller can run against a tree
that has none.

This module is pure standard library so it can be imported from the self-
contained `uv` tool scripts (`spack-db`, `user-stack`) without adding
dependencies.
"""

import json
import os


# Spack dependency edge types.
DEPTYPES = ('build', 'link', 'run')


def index_path(mount):
    """The database file of the Spack tree rooted at ``mount``."""
    return os.path.join(os.path.realpath(mount), '.spack-db', 'index.json')


class Package:
    """A single installed Spack package (one entry in the database)."""

    __slots__ = ('hash', 'name', 'version', 'prefix', 'explicit', '_deps',
                 '_real_prefix')

    def __init__(self, dag_hash, record):
        spec = record.get('spec', {})
        self.hash = dag_hash
        self.name = spec.get('name')
        self.version = _version_str(spec.get('version'))
        self.prefix = record.get('path')
        self.explicit = bool(record.get('explicit'))
        self._real_prefix = None
        # list of (hash, name, (deptype, ...))
        self._deps = []
        for dep in spec.get('dependencies', []) or []:
            params = dep.get('parameters', {}) or {}
            self._deps.append((
                dep.get('hash'),
                dep.get('name'),
                tuple(params.get('deptypes', []) or []),
            ))

    @property
    def real_prefix(self):
        """The install prefix, resolved once and remembered.

        Provenance questions ask "is this prefix under the mount?" for every
        package, sometimes more than once per package, and resolving a path is
        a syscall — on a squashfs, a slow one.
        """
        if self._real_prefix is None and self.prefix:
            self._real_prefix = os.path.realpath(self.prefix)
        return self._real_prefix

    def dep_edges(self, types=None):
        """Return (hash, name, deptypes) edges, optionally filtered by type."""
        if types is None:
            return list(self._deps)
        want = set(types)
        return [e for e in self._deps if not want.isdisjoint(e[2])]

    def short(self):
        return self.hash[:7] if self.hash else '-'

    def label(self):
        return '{}@{}'.format(self.name, self.version)


def _version_str(v):
    """Spack versions are strings, but normalise defensively."""
    if v is None:
        return None
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        # older/newer schemas may wrap the version
        return v.get('string') or v.get('version') or str(v)
    return str(v)


class SpackDB:
    """In-memory view of a Spack ``index.json`` database."""

    def __init__(self, mount):
        self.mount = os.path.realpath(mount)
        self.path = index_path(mount)
        self.version = None
        self.packages = {}          # hash -> Package
        self._by_name = {}          # name -> [hash, ...]

    # -- loading ----------------------------------------------------------

    @classmethod
    def open(cls, mount):
        """Return a loaded SpackDB, or None if there is no readable database.

        Both callers want the same thing — a database if there is one — and
        differ only in what they do without it, so the exists-then-read dance
        lives here rather than in each of them.
        """
        db = cls(mount)
        if not db.exists():
            return None
        try:
            db._read()
        except (OSError, ValueError, KeyError):
            return None
        return db

    def _read(self):
        with open(self.path) as f:
            data = json.load(f)
        database = data['database']
        self.version = database.get('version')
        for dag_hash, record in database.get('installs', {}).items():
            pkg = Package(dag_hash, record)
            self.packages[dag_hash] = pkg
            self._by_name.setdefault(pkg.name, []).append(dag_hash)

    def exists(self):
        return os.path.isfile(self.path)

    # -- lookups ----------------------------------------------------------

    def get(self, dag_hash):
        """Exact hash lookup, or None."""
        return self.packages.get(dag_hash)

    def resolve(self, token):
        """Resolve a token (full hash, name, or hash prefix) to [Package].

        Order of matching: exact full hash, exact package name, hash prefix.
        Name is tried before hash-prefix so a package name that happens to be a
        valid hash prefix still resolves to the package. Returns a list
        (possibly empty, or many for an ambiguous name / prefix).
        """
        if token in self.packages:
            return [self.packages[token]]
        if token in self._by_name:
            return [self.packages[h] for h in self._by_name[token]]
        # hash prefix (spack-style short hashes)
        pref = [h for h in self.packages if h.startswith(token)]
        if pref:
            return [self.packages[h] for h in pref]
        return []

    def all(self, name=None, roots_only=False, internal=None):
        """Return packages, optionally filtered.

        internal: True → only packages installed under the mount; False → only
        external/system packages; None → all.
        """
        out = []
        for pkg in self.packages.values():
            if name and pkg.name != name:
                continue
            if roots_only and not pkg.explicit:
                continue
            if internal is not None and self.is_internal(pkg) != internal:
                continue
            out.append(pkg)
        return sorted(out, key=lambda p: (p.name or '', p.version or ''))

    # -- provenance -------------------------------------------------------

    def is_internal(self, pkg):
        """True if the package was installed by Spack in this tree.

        i.e. its install prefix lies under ``mount``. External packages (glibc,
        the host CUDA driver, ...) are registered in the database with a prefix
        outside the tree (typically ``/usr``) and return False.
        """
        if not pkg or not pkg.prefix:
            return False
        p = pkg.real_prefix
        return p == self.mount or p.startswith(self.mount + os.sep)

    def _owner_by_prefix(self, target):
        """The Package whose install prefix contains ``target``.

        The fallback for a path that carries no store hash. Picks the most
        specific (longest) matching prefix.
        """
        best = None
        best_len = -1
        for pkg in self.packages.values():
            prefix = pkg.real_prefix
            if not prefix:
                continue
            if target == prefix or target.startswith(prefix + os.sep):
                if len(prefix) > best_len:
                    best, best_len = pkg, len(prefix)
        return best

    def owner(self, path):
        """Map a path to the Package that installed it, or None.

        Store directories are named ``<name>-<version>-<hash>``, so the hash in
        the path names the package directly — which is what makes this work for
        a view symlink whose path does not literally start with any install
        prefix. Falls back to a prefix scan when there is no hash to read.
        """
        if not path:
            return None
        real = os.path.realpath(path)
        for part in real.split(os.sep):
            # the 32-char spack hash is the last '-'-separated token
            tail = part.rsplit('-', 1)[-1]
            if len(tail) == 32 and tail in self.packages:
                return self.packages[tail]
        return self._owner_by_prefix(real)

    # -- graph ------------------------------------------------------------

    def dependencies(self, dag_hash, types=None, transitive=False):
        """Return dependency Packages of ``dag_hash``.

        types: iterable of deptypes to follow (default: all).
        transitive: follow edges recursively.
        """
        pkg = self.packages.get(dag_hash)
        if not pkg:
            return []
        if not transitive:
            return [self.packages[h] for h, _, _ in pkg.dep_edges(types)
                    if h in self.packages]
        seen = {}
        stack = [h for h, _, _ in pkg.dep_edges(types)]
        while stack:
            h = stack.pop()
            if h in seen or h not in self.packages:
                continue
            seen[h] = self.packages[h]
            stack.extend(hh for hh, _, _ in self.packages[h].dep_edges(types))
        return list(seen.values())

    def _reverse_edges(self, types=None):
        """Return {hash: [dependent hash, ...]} over the whole database."""
        reverse = {}
        for pkg in self.packages.values():
            for h, _, _ in pkg.dep_edges(types):
                reverse.setdefault(h, []).append(pkg.hash)
        return reverse

    def dependents(self, dag_hash, types=None, transitive=False):
        """Return packages that depend on ``dag_hash`` (reverse edges).

        The reverse index is built once per call and then walked, rather than
        rescanning every package for every hash reached: on a uenv of a few
        hundred packages the difference is a table lookup against a quadratic
        sweep.
        """
        reverse = self._reverse_edges(types)
        seen = {}
        stack = list(reverse.get(dag_hash, ()))
        while stack:
            h = stack.pop()
            if h in seen:
                continue
            seen[h] = self.packages[h]
            if transitive:
                stack.extend(reverse.get(h, ()))
        return list(seen.values())
