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

This module is pure standard library so it can be imported from the self-
contained `uv` tool scripts (`spack-db`, `user-stack`) without adding
dependencies.
"""

import json
import os


# Spack dependency edge types.
DEPTYPES = ('build', 'link', 'run')


class Package:
    """A single installed Spack package (one entry in the database)."""

    __slots__ = ('hash', 'name', 'version', 'prefix', 'explicit',
                 'install_time', '_deps')

    def __init__(self, dag_hash, record):
        spec = record.get('spec', {})
        self.hash = dag_hash
        self.name = spec.get('name')
        self.version = _version_str(spec.get('version'))
        self.prefix = record.get('path')
        self.explicit = bool(record.get('explicit'))
        self.install_time = record.get('installation_time')
        # list of (hash, name, (deptype, ...))
        self._deps = []
        for dep in spec.get('dependencies', []) or []:
            params = dep.get('parameters', {}) or {}
            self._deps.append((
                dep.get('hash'),
                dep.get('name'),
                tuple(params.get('deptypes', []) or []),
            ))

    def dep_edges(self, types=None):
        """Return (hash, name, deptypes) edges, optionally filtered by type."""
        if types is None:
            return list(self._deps)
        want = set(types)
        return [e for e in self._deps if want & set(e[2])]

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
        self.path = os.path.join(self.mount, '.spack-db', 'index.json')
        self.version = None
        self.packages = {}          # hash -> Package
        self._by_name = {}          # name -> [hash, ...]

    # -- loading ----------------------------------------------------------

    @classmethod
    def load(cls, mount):
        db = cls(mount)
        db._read()
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

    def by_name(self, name):
        return [self.packages[h] for h in self._by_name.get(name, [])]

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
        p = os.path.realpath(pkg.prefix)
        return p == self.mount or p.startswith(self.mount + os.sep)

    def owner(self, path):
        """Return the Package whose install prefix contains ``path``.

        Used to map a resolved library path back to its Spack package. Picks
        the most specific (longest) matching prefix.
        """
        if not path:
            return None
        target = os.path.realpath(path)
        best = None
        best_len = -1
        for pkg in self.packages.values():
            if not pkg.prefix:
                continue
            prefix = os.path.realpath(pkg.prefix)
            if target == prefix or target.startswith(prefix + os.sep):
                if len(prefix) > best_len:
                    best, best_len = pkg, len(prefix)
        return best

    def owner_by_hash_in_path(self, path):
        """Map a Spack *store* path to a package via the hash in its dir name.

        Store directories are named ``<name>-<version>-<hash>``; extracting the
        trailing hash is a robust fallback when a symlinked view path does not
        literally start with the install prefix.
        """
        if not path:
            return None
        real = os.path.realpath(path)
        for part in real.split(os.sep):
            # the 32-char spack hash is the last '-'-separated token
            tail = part.rsplit('-', 1)[-1]
            if len(tail) == 32 and tail in self.packages:
                return self.packages[tail]
        return self.owner(real)

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

    def dependents(self, dag_hash, types=None, transitive=False):
        """Return packages that depend on ``dag_hash`` (reverse edges)."""
        direct = {}
        for pkg in self.packages.values():
            for h, _, _ in pkg.dep_edges(types):
                if h == dag_hash:
                    direct[pkg.hash] = pkg
                    break
        if not transitive:
            return list(direct.values())
        seen = dict(direct)
        stack = list(direct)
        while stack:
            cur = stack.pop()
            for pkg in self.packages.values():
                if pkg.hash in seen:
                    continue
                if any(h == cur for h, _, _ in pkg.dep_edges(types)):
                    seen[pkg.hash] = pkg
                    stack.append(pkg.hash)
        return list(seen.values())
