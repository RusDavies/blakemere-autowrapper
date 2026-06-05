# AutoWrapper Backlog

This backlog captures the initial improvement plan for turning `AutoWrapper.py` from a proof of concept into a reliable reusable wrapper/proxy utility.

## Burndown

- Open: 0
- Done: 24
- Total: 24

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

### [x] AW-020 Add TestPyPI publishing workflow and first-run documentation

**Problem:** Production PyPI should not be the first external upload target for a new package.

**Acceptance criteria:**

- Add a separate TestPyPI publishing workflow.
- Document TestPyPI trusted-publisher setup.
- Document manual publishing of the existing `v0.1.0` tag to TestPyPI.
- Document TestPyPI installation verification before production PyPI publishing.

### [x] AW-021 Rename PyPI distribution to blakemere-autowrapper

**Problem:** The repository is named `blakemere-autowrapper`, and Russ wants the published PyPI distribution to use the same name rather than `autowrapper`.

**Acceptance criteria:**

- Change the distribution name to `blakemere-autowrapper`.
- Preserve the Python import path `autowrapper`.
- Bump the package version for the distribution rename.
- Update TestPyPI/PyPI publishing documentation and install commands.

### [x] AW-022 Decide Python 3.8 support vs SPDX license metadata modernization

**Problem:** Current setuptools emits deprecation warnings for table-style `project.license` metadata and license classifiers, but the SPDX-style `license = "MIT"` metadata breaks GitHub Actions wheel builds on Python 3.8 because Python 3.8 resolves to a setuptools line that still expects the older PEP 621 table format.

**Acceptance criteria:**

- Decide whether to keep Python 3.8 support until its broader ecosystem support is no longer worth carrying, or drop Python 3.8 and require a newer setuptools/Python packaging baseline.
- If Python 3.8 stays supported, keep the compatible metadata and tolerate/document the setuptools deprecation warning for now.
- If Python 3.8 support is dropped, update CI, `requires-python`, docs, and package metadata together.
- Keep `LICENSE` included in built distributions.
- Bump the package version only when the chosen package metadata/support-policy change is ready to release.

**Decision:** Keep Python 3.8 support for now and retain the Python 3.8-compatible license metadata form, `license = {file = "LICENSE"}`. The setuptools deprecation warnings for table-style license metadata and the MIT license classifier are accepted until the project drops Python 3.8 or otherwise moves to a newer packaging baseline. Do not modernize the license metadata in isolation; when Python 3.8 is dropped, update `requires-python`, CI, README support docs, license metadata/classifiers, and the package version together.

**Completion notes:** Documented the policy in README and publishing docs. Verified that the build still includes `LICENSE` in both the sdist and wheel. No package version bump was made because this change documents the support policy and does not prepare a new package release.

### [x] AW-023 Update GitHub Actions runtime compatibility before Node 20 removal

**Problem:** GitHub Actions now warns that `actions/checkout@v4` and `actions/setup-python@v5` run on Node.js 20, which will be forced to Node.js 24 by default on 2026-06-16 and removed from runners on 2026-09-16.

**Acceptance criteria:**

- Review whether newer `actions/checkout` and `actions/setup-python` versions are available and suitable.
- Update CI and publish workflows to Node 24-compatible action versions or explicitly test with `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true`.
- Verify CI across the supported Python matrix after the workflow update.

**Completion notes:** Updated CI, PyPI, and TestPyPI workflows to `actions/checkout@v6` and `actions/setup-python@v6`, both of which declare the Node 24 runtime in their action metadata. The PyPI publish action remains on `pypa/gh-action-pypi-publish@release/v1`, whose current release is a composite action rather than a Node 20 JavaScript action.

### [x] AW-024 Restrict CI workflow token permissions

**Problem:** The CI workflow relied on GitHub's default `GITHUB_TOKEN` permissions. Repository or organization defaults can change, so the workflow should explicitly request only read access for normal test/build work.

**Acceptance criteria:**

- Add explicit `permissions: contents: read` to the CI workflow.
- Keep publishing workflows on trusted-publishing `id-token: write` permissions only where required.
- Verify local compile, test, build, twine, wheel-install smoke, and security scanner gates.

**Completion notes:** Hardened `.github/workflows/ci.yml` with explicit read-only contents permissions. Publish workflows already use explicit `contents: read` plus `id-token: write` inside protected PyPI/TestPyPI environments, so no change was needed there.
