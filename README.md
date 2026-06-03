# AutoWrapper

AutoWrapper is a small Python helper for building wrapper/proxy objects around another object's methods.

It lets a wrapper class expose selected methods from a target object and optionally route method calls through pre/post/exception hooks. This is useful for lightweight instrumentation such as logging, tracing, metrics, access checks, or debugging wrappers.

## Current status

This project is still small and intentionally direct: one implementation module, `AutoWrapper.py`, plus a `unittest` test suite.

Implemented behavior:

- Wrap methods from a target object onto a wrapper instance.
- Call target-bound methods so target instance state is preserved.
- Support optional hints for selecting which methods to proxy and wrap.
- Support no-hints mode, which proxies and wraps all public discovered methods.
- Discover inherited instance methods.
- Skip private/dunder methods by default, with explicit hint opt-in.
- Preserve useful method metadata for wrapped methods via `functools.wraps()`.
- Provide pre, post, and exception hooks with method context.

## Basic usage

```python
from AutoWrapper import AutoWrapper


class Example:
    def __init__(self):
        self.count = 0

    def increment(self, amount=1):
        self.count += amount
        return self.count


class WrappedExample(AutoWrapper):
    def __init__(self, target):
        self.events = []
        self.build_wrapper(
            target,
            hints={"increment": {"proxy": True, "wrap": True}},
        )

    def _pre_method_hook(self, method_name, method, args, kwargs):
        self.events.append(("pre", method_name, args, kwargs))

    def _post_method_hook(self, method_name, method, args, kwargs, result):
        self.events.append(("post", method_name, result))

    def _exception_method_hook(self, method_name, method, args, kwargs, exc):
        self.events.append(("exception", method_name, exc))


target = Example()
wrapper = WrappedExample(target)

assert wrapper.increment(amount=2) == 2
assert target.count == 2
assert wrapper.events == [
    ("pre", "increment", (), {"amount": 2}),
    ("post", "increment", 2),
]
```

## Hint semantics

`build_wrapper(target, hints=...)` accepts a dictionary keyed by method name.

Supported keys:

- `proxy`: expose this method on the wrapper instance.
- `wrap`: route the proxied method through the hook methods.

Behavior:

- `hints is None`: proxy and wrap every public discovered method.
- `proxy: True`: expose the method on the wrapper.
- `proxy` absent or false: do not expose the method, even if `wrap: True`.
- `wrap: True`: call `_pre_method_hook()` before the target method and `_post_method_hook()` after it succeeds.
- `wrap` absent or false: expose the target-bound method directly without hooks.
- Methods absent from a supplied `hints` dictionary are not proxied.
- Private methods whose names begin with `_` are skipped by default, but can be explicitly proxied with hints.

## Hook signatures

Override these methods in your wrapper subclass when you need behavior around wrapped calls:

```python
def _pre_method_hook(self, method_name, method, args, kwargs):
    pass

def _post_method_hook(self, method_name, method, args, kwargs, result):
    pass

def _exception_method_hook(self, method_name, method, args, kwargs, exc):
    pass
```

Exceptions raised by wrapped target methods call `_exception_method_hook()` and then propagate unchanged.

## Running tests

This project currently uses the Python standard-library `unittest` framework, so no test dependency installation is required.

From a clean checkout, run:

```bash
python -m unittest discover -s tests -v
```

You can also run the inline example in the implementation module:

```bash
python AutoWrapper.py
```

## Repository layout

```text
AutoWrapper.py              # implementation and tiny inline example
__init__.py                 # placeholder package marker
tests/test_autowrapper.py   # unittest coverage
BACKLOG.md                  # project improvement backlog
```

## Known next step

The remaining structural improvement is packaging: add `pyproject.toml`, choose a lowercase package/module layout, and define install metadata.
