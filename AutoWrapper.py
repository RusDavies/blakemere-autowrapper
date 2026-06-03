import inspect
from types import FunctionType
from functools import wraps

class AutoWrapper():
    @staticmethod
    def getMethods2Wrap(class_type, hints=None):
        methods = inspect.getmembers(class_type, predicate=inspect.isfunction)
        if (hints == None):
            # With no hints, wrap all public discovered functions.
            results = [(name, att) for (name, att) in methods if not name.startswith('_')]
        else:
            # With hints, explicit proxy opt-in can include private methods.
            results = [
                (name, att) for (name, att) in methods
                if hints.get(name, {}).get('proxy', False)
            ]
        return results

    def build_wrapper(self, class_to_wrap, hints=None):
        """Build proxy methods for ``class_to_wrap``.

        Hint semantics:

        * ``hints is None``: every public method discovered by
          ``getMethods2Wrap`` is proxied and wrapped with the pre/post hooks;
          names beginning with ``_`` are skipped by default.
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
        """
        self._wrapped = class_to_wrap
        class_type = type(class_to_wrap)
        wrap_by_default = hints is None
        for (attributeName, attribute) in __class__.getMethods2Wrap(class_type, hints):
            bound_attribute = getattr(class_to_wrap, attributeName)
            should_wrap = wrap_by_default or hints.get(attributeName, {}).get('wrap', False)
            if ((isinstance(attribute, FunctionType) == True) & (should_wrap == True)):
                bound_attribute = self._wrapper(bound_attribute)
            self.__dict__[attributeName] = bound_attribute

    def _wrapper(self, method):
        @wraps(method)
        def wrapped(*args, **kwargs):
            self._pre_method_hook(method, *args, **kwargs)
            result = method(*args, **kwargs)
            self._post_method_hook(method, *args, **kwargs)
            return result
        return wrapped

    def _pre_method_hook(self, method, *args, **kwargs):
        pass

    def _post_method_hook(self, method, *args, **kwargs):
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

        def _pre_method_hook(self, method, *args, **kwargs):
            print("_pre_method_hook() called for {!r}".format(method.__name__))

        def _post_method_hook(self, method, *args, **kwargs):
            print("_post_method_hook() called for {!r}".format(method.__name__))


    test = WExample()
    test.methodA()

    # Results:
    # _pre_method_hook() called for 'methodA'
    # Method A called
    # _post_method_hook() called for 'methodA'
