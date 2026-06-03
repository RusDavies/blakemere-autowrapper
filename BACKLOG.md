# AutoWrapper Backlog

This backlog captures the initial improvement plan for turning `AutoWrapper.py` from a proof of concept into a reliable reusable wrapper/proxy utility.

## Burndown

- Open: 0
- Done: 19
- Total: 19

## Items

### [x] AW-001 Fix core wrapped-object method binding

**Problem:** Wrapped methods currently receive the `AutoWrapper` instance as `self`, not the object being wrapped. This only works for methods that do not access instance state.

**Acceptance criteria:**

- `build_wrapper()` stores the target object, e.g. `self._wrapped`.
- Proxied methods are bound from the target object using `getattr(target, method_name)`.
- A wrapped method that reads or writes target instance state behaves correctly.
- Regression test covers a target method using `self.some_attr`.

### [x] AW-002 Make hints optional and define defaults

**Problem:** `hints=None` is partly supported by discovery but later code calls `hints.get(...)`, which will fail.

**Acceptance criteria:**

- Calling `build_wrapper(target)` without hints works.
- Default behavior is documented.
- Tests cover no-hints behavior.

### [x] AW-003 Clarify proxy/wrap configuration semantics

**Problem:** The current `hints` structure is workable but underspecified.

**Acceptance criteria:**

- Document supported hint keys: `proxy` and `wrap`.
- Define what happens when a method is absent from hints.
- Preserve backward compatibility with current hint dictionaries.
- Add tests for proxy-only, wrap-only/default, and excluded methods.

### [x] AW-004 Support inherited methods

**Problem:** Method discovery uses `class_type.__dict__`, so inherited methods are ignored.

**Acceptance criteria:**

- Inherited instance methods can be proxied/wrapped.
- Direct class methods still work.
- Tests cover a subclass inheriting a method from a parent class.

### [x] AW-005 Skip private and dunder methods by default

**Problem:** Auto-proxying implementation details or Python magic methods can create surprising behavior.

**Acceptance criteria:**

- Default discovery excludes names beginning with `_`.
- Explicit hints can include private methods if needed.
- Tests cover skipped private methods and explicit inclusion.

### [x] AW-006 Fix wrapper argument handling

**Problem:** `_wrapper()` calls `method(self, *args, *kwargs)`, which is incorrect for keyword arguments.

**Acceptance criteria:**

- Wrapped methods receive positional and keyword arguments correctly.
- Tests cover keyword-only and mixed positional/keyword calls.

### [x] AW-007 Add useful hook signatures and exception handling

**Problem:** Hooks receive limited context and there is no exception hook.

**Acceptance criteria:**

- Pre-hook receives method name, method, args, and kwargs.
- Post-hook receives method name, method, args, kwargs, and result.
- Exception hook receives method name, method, args, kwargs, and exception.
- Exceptions still propagate unless explicitly documented otherwise.
- Tests cover pre/post ordering and exception handling.

### [x] AW-008 Preserve method metadata

**Problem:** Generated wrappers should remain debuggable and introspection-friendly.

**Acceptance criteria:**

- Wrapped proxy methods preserve useful `__name__`, `__doc__`, and related metadata where practical.
- Tests or direct inspection verify metadata preservation.

### [x] AW-009 Add project packaging structure

**Problem:** The repository is currently just a loose module and empty `__init__.py`.

**Acceptance criteria:**

- Add `pyproject.toml`.
- Decide package/module layout, preferably lowercase import path.
- Add basic package metadata.
- Keep installation simple for local development.

### [x] AW-010 Add README and test suite

**Problem:** The project has no external-facing documentation or verification gate.

**Acceptance criteria:**

- Add README with purpose, installation, and usage examples.
- Add tests under `tests/`.
- Document and run the chosen verification command.
- Ensure the project can be validated from a clean checkout.

## Suggested implementation order

1. AW-001 Fix core wrapped-object method binding.
2. AW-006 Fix wrapper argument handling.
3. AW-002 Make hints optional and define defaults.
4. AW-003 Clarify proxy/wrap configuration semantics.
5. AW-004 Support inherited methods.
6. AW-005 Skip private and dunder methods by default.
7. AW-007 Add useful hook signatures and exception handling.
8. AW-008 Preserve method metadata.
9. AW-010 Add README and test suite.
10. AW-009 Add project packaging structure.

## Next improvement batch

### [x] AW-011 Add LICENSE file

**Problem:** `pyproject.toml` declares MIT licensing, but the repository does not include a `LICENSE` file.

**Acceptance criteria:**

- Add an MIT `LICENSE` file.
- Ensure package metadata and README licensing notes are consistent.

### [x] AW-012 Add CI workflow

**Problem:** Tests currently run locally only; regressions will not be caught automatically on GitHub.

**Acceptance criteria:**

- Add a GitHub Actions workflow.
- Run the unittest suite.
- Run Python compile checks.
- Build/package validation runs if practical.

### [x] AW-013 Decide and test classmethod/staticmethod behavior

**Problem:** Static methods are currently discovered, but class methods are skipped because discovery only includes `inspect.isfunction` results.

**Acceptance criteria:**

- Document intended behavior for `@staticmethod` and `@classmethod`.
- Add explicit tests for static methods.
- Add explicit tests for class methods or document that they are unsupported.
- Implement classmethod support if supported behavior is chosen.

### [x] AW-014 Add collision detection for wrapper attribute assignment

**Problem:** `build_wrapper()` writes proxied methods directly into `self.__dict__`, which can overwrite wrapper state or existing wrapper methods.

**Acceptance criteria:**

- Detect collisions before assigning proxied methods to the wrapper instance.
- Raise a clear exception by default when a proxied name already exists on the wrapper.
- Allow safe non-colliding proxy assignment to keep working.
- Tests cover collisions with wrapper instance attributes and wrapper methods.

### [x] AW-015 Add type hints and snake_case API alias

**Problem:** Public APIs are untyped and `getMethods2Wrap` is non-idiomatic Python naming.

**Acceptance criteria:**

- Add type hints for public methods and hooks.
- Add `get_methods_to_wrap` as a snake_case alias or replacement while preserving compatibility.
- Update docs/tests to prefer the snake_case name.

### [x] AW-016 Document standalone function support decision

**Problem:** The project wraps object methods, not standalone functions, but the scope is not stated explicitly.

**Acceptance criteria:**

- Document whether standalone function wrapping is supported.
- If unsupported, state the limitation clearly in README.
- If supported, add implementation and tests.

### [x] AW-017 Fix Python 3.8 runtime typing compatibility

**Problem:** GitHub Actions showed Python 3.8 failing at import time because `collections.abc.Mapping` and `collections.abc.Callable` are not runtime-subscriptable there, even with postponed annotations.

**Acceptance criteria:**

- Import-time type aliases work on Python 3.8.
- CI matrix passes on supported Python versions.
- Existing typed public API remains intact.

### [x] AW-018 Fix Python 3.8 runtime tuple type alias compatibility

**Problem:** GitHub Actions showed Python 3.8 still failing at import time because `tuple[...]` is not runtime-subscriptable in Python 3.8 when used in a type alias.

**Acceptance criteria:**

- Runtime type aliases avoid Python 3.9+ builtin generic syntax.
- CI matrix passes on supported Python versions.

### [x] AW-019 Set up PyPI publishing workflow and documentation

**Problem:** The package is release-tagged on GitHub but not yet configured with a safe repeatable PyPI publishing process.

**Acceptance criteria:**

- Add a GitHub Actions workflow for PyPI trusted publishing.
- Document one-time PyPI trusted-publisher setup.
- Document how to publish the existing `v0.1.0` release.
- Verify package metadata and build artifacts locally.
