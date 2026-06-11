# AutoWrapper

AutoWrapper is a small Python helper for building wrapper/proxy objects around another object's methods.

It lets a wrapper class expose selected methods from a target object and optionally route method calls through pre/post/exception hooks. This is useful for lightweight instrumentation such as logging, tracing, metrics, access checks, or debugging wrappers.

## Current status

This project is still small and intentionally direct: one implementation module, `AutoWrapper.py`, a lowercase compatibility import module, packaging metadata, and a `unittest` test suite.

Implemented behavior:

- Wrap methods from a target object onto a wrapper instance.
- Call target-bound methods so target instance state is preserved.
- Support optional hints for selecting which methods to proxy and wrap.
- Support no-hints mode, which proxies and wraps all public discovered methods.
- Discover inherited instance methods, static methods, and class methods.
- Skip private/dunder methods by default, with explicit hint opt-in.
- Preserve useful method metadata for wrapped methods via `functools.wraps()`.
- Provide pre, post, and exception hooks with method context.
- Reject proxied method names that would overwrite wrapper attributes or methods.
- Provide typed public methods and prefer the snake_case `get_methods_to_wrap()` discovery API while preserving `getMethods2Wrap()` compatibility.

## Basic usage

```python
from autowrapper import AutoWrapper


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


## Scope: object methods, not standalone functions

AutoWrapper is intentionally scoped to wrapping methods discovered from a target object. It supports instance methods, inherited methods, static methods, and class methods on that target object's class.

Standalone/free functions are out of scope for now. If you need to wrap a free function, use a normal decorator directly or place the function behind a small object method before using AutoWrapper.

## Method discovery API

The preferred public discovery helper is:

```python
AutoWrapper.get_methods_to_wrap(TargetClass, hints=None)
```

The original spelling remains available for compatibility:

```python
AutoWrapper.getMethods2Wrap(TargetClass, hints=None)
```

## Hint semantics

`build_wrapper(target, hints=...)` accepts a dictionary keyed by method name.

Supported keys:

- `proxy`: expose this method on the wrapper instance.
- `wrap`: route the proxied method through the hook methods.

Behavior:

- `hints is None`: proxy and wrap every public discovered instance, static, and class method.
- `proxy: True`: expose the method on the wrapper.
- `proxy` absent or false: do not expose the method, even if `wrap: True`.
- `wrap: True`: call `_pre_method_hook()` before the target method and `_post_method_hook()` after it succeeds.
- `wrap` absent or false: expose the target-bound method directly without hooks.
- Methods absent from a supplied `hints` dictionary are not proxied.
- Static methods and class methods are supported and can be proxied/wrapped like instance methods.
- Private methods whose names begin with `_` are skipped by default, but can be explicitly proxied with hints.
- Proxied method names that collide with existing wrapper attributes or methods raise `AttributeError`.

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

## Installation

Once published to PyPI, install with:

```bash
python -m pip install blakemere-autowrapper
```

For local development from a clean checkout:

```bash
python -m pip install -e .
```

The PyPI distribution name is `blakemere-autowrapper`. The preferred import path is lowercase:

```python
from autowrapper import AutoWrapper
```

The original import path remains available for compatibility:

```python
from AutoWrapper import AutoWrapper
```

## Running tests

This project currently uses the Python standard-library `unittest` framework, so no test dependency installation is required.

Supported Python versions currently track the CI matrix: Python 3.9 through 3.13.

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
autowrapper.py              # lowercase import compatibility module
pyproject.toml              # packaging metadata
__init__.py                 # placeholder package marker
tests/test_autowrapper.py   # unittest coverage
BACKLOG.md                  # project improvement backlog
```

## Packaging note

`pyproject.toml` packages both modules:

- `autowrapper`: preferred lowercase import path.
- `AutoWrapper`: original compatibility import path.

The project uses modern SPDX license metadata and explicitly includes the license file in built distributions:

```toml
license = "MIT"
license-files = ["LICENSE"]
```

The build backend requires `setuptools>=77.0.3`, which provides the PEP 639/SPDX license metadata support used here. The built wheel includes the `LICENSE` file under `.dist-info/licenses/`.

## License

MIT. See [LICENSE](LICENSE).
