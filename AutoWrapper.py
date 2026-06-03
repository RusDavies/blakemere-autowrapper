from __future__ import annotations

import inspect
from functools import wraps
from typing import Any, Callable, Mapping, Optional

HintConfig = Mapping[str, bool]
Hints = Mapping[str, HintConfig]
MethodEntry = tuple[str, Callable[..., Any]]


class AutoWrapper:
    @staticmethod
    def get_methods_to_wrap(class_type: type, hints: Optional[Hints] = None) -> list[MethodEntry]:
        methods = inspect.getmembers(
            class_type,
            predicate=lambda att: inspect.isfunction(att) or inspect.ismethod(att),
        )
        if hints is None:
            # With no hints, wrap all public discovered functions.
            results = [(name, att) for (name, att) in methods if not name.startswith('_')]
        else:
            # With hints, explicit proxy opt-in can include private methods.
            results = [
                (name, att) for (name, att) in methods
                if hints.get(name, {}).get('proxy', False)
            ]
        return results

    # Backward-compatible alias for the original public API spelling.
    getMethods2Wrap = get_methods_to_wrap

    def build_wrapper(self, class_to_wrap: object, hints: Optional[Hints] = None) -> None:
        """Build proxy methods for ``class_to_wrap``.

        Hint semantics:

        * ``hints is None``: every public method discovered by
          ``get_methods_to_wrap`` is proxied and wrapped with the pre/post
          hooks; names beginning with ``_`` are skipped by default.
        * ``proxy: True``: expose that method on this wrapper instance. This
          explicit opt-in can include private methods.
        * ``proxy`` absent or false: do not expose that method on this wrapper
          instance, even if ``wrap`` is true.
        * ``wrap: True``: proxy the method through ``_pre_method_hook`` and
          ``_post_method_hook``.
        * ``wrap`` absent or false: proxy the target-bound method directly
          without hook calls.
        * Methods absent from ``hints`` are not proxied when a hints dictionary
          is supplied.
        * Instance methods, static methods, class methods, and inherited
          methods are discoverable.
        * Wrapped method exceptions call ``_exception_method_hook`` and then
          propagate unchanged.
        * Proxied method names must not collide with existing wrapper
          attributes or methods.
        """
        self._wrapped = class_to_wrap
        class_type = type(class_to_wrap)
        wrap_by_default = hints is None
        for (attributeName, attribute) in self.get_methods_to_wrap(class_type, hints):
            bound_attribute = getattr(class_to_wrap, attributeName)
            should_wrap = wrap_by_default or hints.get(attributeName, {}).get('wrap', False)
            if hasattr(self, attributeName):
                raise AttributeError(
                    "Cannot proxy method {!r}: wrapper already has an "
                    "attribute with that name".format(attributeName)
                )
            if callable(bound_attribute) and should_wrap:
                bound_attribute = self._wrapper(bound_attribute)
            self.__dict__[attributeName] = bound_attribute

    def _wrapper(self, method: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(method)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            method_name = method.__name__
            self._pre_method_hook(method_name, method, args, kwargs)
            try:
                result = method(*args, **kwargs)
            except Exception as exc:
                self._exception_method_hook(method_name, method, args, kwargs, exc)
                raise
            self._post_method_hook(method_name, method, args, kwargs, result)
            return result
        return wrapped

    def _pre_method_hook(
        self,
        method_name: str,
        method: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None:
        pass

    def _post_method_hook(
        self,
        method_name: str,
        method: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        result: Any,
    ) -> None:
        pass

    def _exception_method_hook(
        self,
        method_name: str,
        method: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        exc: Exception,
    ) -> None:
        pass


if __name__ == '__main__':
    # Example usage
    class Example:
        def methodA(self):
            print("Method A called")

        def methodB(self):
            print("Method B called")

    class WExample(AutoWrapper):
        def __init__(self):
            self.example = Example()
            hints = { 'methodA': {'proxy': True, 'wrap': True},
                      'methodB': {'proxy': True, 'wrap': False} }
            self.build_wrapper( self.example, hints=hints )

        def _pre_method_hook(self, method_name, method, args, kwargs):
            print("_pre_method_hook() called for {!r}".format(method_name))

        def _post_method_hook(self, method_name, method, args, kwargs, result):
            print("_post_method_hook() called for {!r}".format(method_name))


    test = WExample()
    test.methodA()

    # Results:
    # _pre_method_hook() called for 'methodA'
    # Method A called
    # _post_method_hook() called for 'methodA'
