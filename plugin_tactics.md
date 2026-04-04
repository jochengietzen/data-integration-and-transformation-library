# Plugin Tactics for DITL

## Current State

The codebase already has strong foundations for plugins through its **registration pattern**:
- `Engine.register_data_type()`, `register_read_method()`, `register_write_method()`
- `Schema.register_from_engine_schema()`
- `DataType.register_from_and_to_methods()`
- `TransformationManager.load_all_transformations()` (dynamic import via `pkgutil`)

The main coupling issue: `PolarsEngine` lives inside `src/ditl/engines/` and `PolarsEngine.setup()` is called at import time (line 109), making `polars` a hard dependency of the core library.

---

## Plugin Approaches

### 1. Python Entry Points (Recommended)

The standard mechanism for Python plugin systems. Each plugin package declares an entry point in its `pyproject.toml`, and the core discovers them at runtime.

**How it works:**

Core (`ditl`) defines a group name, e.g. `ditl.engines`, and discovers plugins:

```python
# ditl/engines/__init__.py
from importlib.metadata import entry_points

def load_engines():
    for ep in entry_points(group="ditl.engines"):
        engine_class = ep.load()  # imports the module, triggers setup()
```

A plugin package (`ditl-polars`) declares:

```toml
# ditl-polars/pyproject.toml
[project.entry-points."ditl.engines"]
polars = "ditl_polars.engine:PolarsEngine"
```

**Pros:**
- Industry standard (`pytest`, `flake8`, `tox` all use this)
- Zero config for users — `pip install ditl-polars` is enough
- Auto-discovery, no manual imports needed
- Clean separation: `polars` is only a dependency of `ditl-polars`, not `ditl`
- Multiple plugin types possible: `ditl.engines`, `ditl.data_types`, `ditl.faker_types`

**Cons:**
- Requires packages to be installed (not just on `sys.path`)
- Slightly more complex packaging setup

---

### 2. Explicit Registration API (Simplest)

Keep the current pattern but make it the public API. Users import and call `setup()` manually.

**How it works:**

```python
# User code
from ditl_polars import PolarsEngine
PolarsEngine.setup()  # registers everything
```

The core removes the auto-call to `setup()` and drops polars from its dependencies.

**Pros:**
- Already 90% implemented in the codebase
- Easiest to understand and debug
- No magic — explicit is better than implicit

**Cons:**
- Users must remember to call `setup()` before using an engine
- No auto-discovery

---

### 3. Hybrid: Entry Points + Explicit Registration

Combine both: auto-discover installed plugins via entry points, but also allow manual `Engine.register(MyCustomEngine)` for ad-hoc or development use.

```python
# ditl/engines/__init__.py
def discover_engines():
    """Auto-load all installed engine plugins."""
    for ep in entry_points(group="ditl.engines"):
        engine_cls = ep.load()
        if hasattr(engine_cls, 'setup'):
            engine_cls.setup()
```

This gives the best of both worlds.

---

### 4. Module-path Discovery (like `load_all_transformations`)

The existing `TransformationManager.load_all_transformations(module_name)` uses `pkgutil.walk_packages`. This could be generalized:

```python
# Auto-import all ditl_* packages
import pkgutil
for importer, modname, ispkg in pkgutil.iter_modules():
    if modname.startswith("ditl_"):
        importlib.import_module(modname)
```

**Pros:** Simple, no entry points needed
**Cons:** Fragile naming convention, imports everything at startup, hard to control load order

---

## What a `ditl-polars` Plugin Would Look Like (Entry Points approach)

```
ditl-polars/
├── pyproject.toml
└── src/
    └── ditl_polars/
        ├── __init__.py
        ├── engine.py          # PolarsEngine class (moved from ditl)
        └── data_types.py      # Optional: polars-specific types
```

**`pyproject.toml`:**
```toml
[project]
name = "ditl-polars"
dependencies = ["ditl", "polars>=1.0"]

[project.entry-points."ditl.engines"]
polars = "ditl_polars.engine:PolarsEngine"
```

**Changes to core `ditl`:**
1. Remove `polars` from core dependencies
2. Remove `engines/polars_engine.py`
3. Add discovery in `engines/__init__.py` or a `ditl.plugins` module
4. Optionally add a `ditl[polars]` extra that depends on `ditl-polars` for backwards compat

---

## What Needs Refactoring in Core

Regardless of approach, a few things need attention:

| Issue | Location | Action |
|-------|----------|--------|
| `registered_types` is a shared `ClassVar` dict on `Engine` base | `engines/base.py:11` | Each engine subclass needs its own copy, or key by `engine_identifier` |
| `registered_read/write_methods` uses `defaultdict` on the base class | `engines/base.py:12-13` | Already keyed by `engine_identifier` — this is fine |
| `PolarsEngine.setup()` auto-called at import | `polars_engine.py:109` | Move to plugin entry point or explicit call |
| `print()` statements in `_from_engine_schema` | `polars_engine.py:22-23` | Remove (pre-commit will catch these) |
| Core imports `polars` transitively | `pyproject.toml` | Move to optional/plugin dependency |

---

## Extras Strategies

Both strategies below use `[project.optional-dependencies]` so that users can install engine support via `pip install ditl[polars]`. They differ in where the engine code lives.

### Strategy A: Extras within a single package (monorepo)

Keep the engine code inside `ditl` but make the heavy dependencies optional:

```toml
# ditl/pyproject.toml
[project]
dependencies = [
    "faker>=40.1.2",
    "networkx>=3.4.2",
    "pydantic>=2.11.5",
    "pyyaml>=6.0.2",
]

[project.optional-dependencies]
polars = ["polars>=1.34.0"]
pandas = ["pandas>=2.3.1"]
all = ["ditl[polars]", "ditl[pandas]"]
```

The engine module guards the import:

```python
# ditl/engines/polars_engine.py
try:
    import polars as pl
except ImportError as e:
    raise ImportError(
        "PolarsEngine requires polars. Install it with: pip install ditl[polars]"
    ) from e
```

`setup()` is no longer called at import time. Instead, a discovery function loads only engines whose dependencies are available.

**Pros:** Simplest to implement, single repo, single package, familiar to users.
**Cons:** Engine code still lives in the core package, just with guarded imports. Not truly decoupled.

---

### Strategy B: Extras that install separate plugin packages

Combines extras with the entry points approach. The core package defines extras that pull in separate plugin packages:

```toml
# ditl/pyproject.toml
[project]
dependencies = [
    "faker>=40.1.2",
    "networkx>=3.4.2",
    "pydantic>=2.11.5",
    "pyyaml>=6.0.2",
]

[project.optional-dependencies]
polars = ["ditl-polars>=0.1.0"]
pandas = ["ditl-pandas>=0.1.0"]
all = ["ditl[polars]", "ditl[pandas]"]
```

```toml
# ditl-polars/pyproject.toml
[project]
name = "ditl-polars"
dependencies = ["ditl>=0.1.0", "polars>=1.34.0"]

[project.entry-points."ditl.engines"]
polars = "ditl_polars.engine:PolarsEngine"
```

Users get the same install UX:

```bash
pip install ditl[polars]     # installs ditl + ditl-polars + polars
pip install ditl[all]        # installs everything
```

But the engine code is fully decoupled — `ditl-polars` is its own package with its own repo/directory, and entry points handle auto-discovery.

**Pros:** True decoupling, third parties can publish their own engines, core stays lean, same user-facing install command.
**Cons:** More packaging overhead, need to manage version compatibility between packages.

---

### Migration Path: A to B

Strategy A and B share the same user-facing install command (`pip install ditl[polars]`), so you can start with A and graduate to B later without breaking users. The transition is:

1. Extract engine code into a separate `ditl-polars` package
2. Change the extra from `polars = ["polars>=1.34.0"]` to `polars = ["ditl-polars>=0.1.0"]`
3. Add entry point declaration in `ditl-polars/pyproject.toml`
4. Remove engine file from core

The install command stays identical throughout.

---

## Recommendation

**Go with approach 3 (Hybrid)** and start by extracting `PolarsEngine` as the first plugin. The entry points mechanism is battle-tested, and keeping explicit registration as a fallback means users can always manually wire things up during development. The registration pattern already built maps perfectly onto this — `setup()` is essentially the plugin's `activate` hook.
º