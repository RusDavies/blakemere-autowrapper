import unittest

from AutoWrapper import AutoWrapper


class StatefulTarget:
    def __init__(self):
        self.value = 3

    def read_value(self):
        return self.value

    def add_to_value(self, amount):
        self.value += amount
        return self.value

    def format_values(self, prefix, value, *, suffix=""):
        return f"{prefix}:{value}{suffix}"

    def keyword_only_total(self, *, first, second=0):
        return first + second


class RecordingWrapper(AutoWrapper):
    def __init__(self, target):
        self.hook_calls = []
        self.build_wrapper(
            target,
            hints={
                "read_value": {"proxy": True, "wrap": True},
                "add_to_value": {"proxy": True, "wrap": True},
                "format_values": {"proxy": True, "wrap": True},
                "keyword_only_total": {"proxy": True, "wrap": True},
            },
        )

    def _pre_method_hook(self, method, *args, **kwargs):
        self.hook_calls.append(("pre", method.__name__))

    def _post_method_hook(self, method, *args, **kwargs):
        self.hook_calls.append(("post", method.__name__))


class DefaultHintsWrapper(AutoWrapper):
    def __init__(self, target):
        self.hook_calls = []
        self.build_wrapper(target)

    def _pre_method_hook(self, method, *args, **kwargs):
        self.hook_calls.append(("pre", method.__name__))

    def _post_method_hook(self, method, *args, **kwargs):
        self.hook_calls.append(("post", method.__name__))


class ConfiguredHintsWrapper(AutoWrapper):
    def __init__(self, target):
        self.hook_calls = []
        self.build_wrapper(
            target,
            hints={
                "read_value": {"proxy": True},
                "add_to_value": {"proxy": True, "wrap": True},
                "keyword_only_total": {"proxy": False, "wrap": True},
            },
        )

    def _pre_method_hook(self, method, *args, **kwargs):
        self.hook_calls.append(("pre", method.__name__))

    def _post_method_hook(self, method, *args, **kwargs):
        self.hook_calls.append(("post", method.__name__))


class AutoWrapperBindingTests(unittest.TestCase):
    def test_wrapped_method_reads_state_from_target_object(self):
        target = StatefulTarget()
        wrapper = RecordingWrapper(target)

        self.assertIs(wrapper._wrapped, target)
        self.assertEqual(wrapper.read_value(), 3)
        self.assertEqual(
            wrapper.hook_calls,
            [("pre", "read_value"), ("post", "read_value")],
        )

    def test_wrapped_method_writes_state_to_target_object(self):
        target = StatefulTarget()
        wrapper = RecordingWrapper(target)

        self.assertEqual(wrapper.add_to_value(4), 7)
        self.assertEqual(target.value, 7)
        self.assertFalse(hasattr(wrapper, "value"))

    def test_wrapped_method_forwards_mixed_positional_and_keyword_arguments(self):
        target = StatefulTarget()
        wrapper = RecordingWrapper(target)

        self.assertEqual(
            wrapper.format_values("item", value=42, suffix="!"),
            "item:42!",
        )

    def test_wrapped_method_forwards_keyword_only_arguments(self):
        target = StatefulTarget()
        wrapper = RecordingWrapper(target)

        self.assertEqual(wrapper.keyword_only_total(first=5, second=8), 13)

    def test_build_wrapper_without_hints_proxies_and_wraps_discovered_methods(self):
        target = StatefulTarget()
        wrapper = DefaultHintsWrapper(target)

        self.assertEqual(wrapper.read_value(), 3)
        self.assertEqual(wrapper.add_to_value(2), 5)
        self.assertEqual(target.value, 5)
        self.assertEqual(
            wrapper.hook_calls,
            [
                ("pre", "read_value"),
                ("post", "read_value"),
                ("pre", "add_to_value"),
                ("post", "add_to_value"),
            ],
        )

    def test_hint_proxy_true_without_wrap_proxies_without_hooks(self):
        target = StatefulTarget()
        wrapper = ConfiguredHintsWrapper(target)

        self.assertEqual(wrapper.read_value(), 3)
        self.assertEqual(wrapper.hook_calls, [])

    def test_hint_proxy_and_wrap_true_proxies_with_hooks(self):
        target = StatefulTarget()
        wrapper = ConfiguredHintsWrapper(target)

        self.assertEqual(wrapper.add_to_value(2), 5)
        self.assertEqual(
            wrapper.hook_calls,
            [("pre", "add_to_value"), ("post", "add_to_value")],
        )

    def test_methods_absent_from_hints_are_not_proxied(self):
        target = StatefulTarget()
        wrapper = ConfiguredHintsWrapper(target)

        self.assertFalse(hasattr(wrapper, "format_values"))

    def test_wrap_true_without_proxy_true_is_not_proxied(self):
        target = StatefulTarget()
        wrapper = ConfiguredHintsWrapper(target)

        self.assertFalse(hasattr(wrapper, "keyword_only_total"))


if __name__ == "__main__":
    unittest.main()
