# AutoWrapper Backlog

This backlog captures the initial improvement plan for turning `AutoWrapper.py` from a proof of concept into a reliable reusable wrapper/proxy utility.

## Burndown

- Open: 6
- Done: 4
- Total: 10

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

### [ ] AW-004 Support inherited methods

**Problem:** Method discovery uses `class_type.__dict__`, so inherited methods are ignored.

**Acceptance criteria:**

- Inherited instance methods can be proxied/wrapped.
- Direct class methods still work.
- Tests cover a subclass inheriting a method from a parent class.

### [ ] AW-005 Skip private and dunder methods by default

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

### [ ] AW-007 Add useful hook signatures and exception handling

**Problem:** Hooks receive limited context and there is no exception hook.

**Acceptance criteria:**

- Pre-hook receives method name, method, args, and kwargs.
- Post-hook receives method name, method, args, kwargs, and result.
- Exception hook receives method name, method, args, kwargs, and exception.
- Exceptions still propagate unless explicitly documented otherwise.
- Tests cover pre/post ordering and exception handling.

### [ ] AW-008 Preserve method metadata

**Problem:** Generated wrappers should remain debuggable and introspection-friendly.

**Acceptance criteria:**

- Wrapped proxy methods preserve useful `__name__`, `__doc__`, and related metadata where practical.
- Tests or direct inspection verify metadata preservation.

### [ ] AW-009 Add project packaging structure

**Problem:** The repository is currently just a loose module and empty `__init__.py`.

**Acceptance criteria:**

- Add `pyproject.toml`.
- Decide package/module layout, preferably lowercase import path.
- Add basic package metadata.
- Keep installation simple for local development.

### [ ] AW-010 Add README and test suite

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
