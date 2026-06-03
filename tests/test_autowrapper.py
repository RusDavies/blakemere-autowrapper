import unittest

from AutoWrapper import AutoWrapper
from autowrapper import AutoWrapper as LowercaseAutoWrapper


class BaseTarget:
    def inherited_value(self):
        return f"inherited:{self.value}"


class StatefulTarget(BaseTarget):
    def __init__(self):
        self.value = 3

    def read_value(self):
        return self.value

    def add_to_value(self, amount):
        self.value += amount
        return self.value

    def format_values(self, prefix, value, *, suffix=""):
        """Format values for metadata-preservation tests."""
        return f"{prefix}:{value}{suffix}"

    def keyword_only_total(self, *, first, second=0):
        return first + second

    @staticmethod
    def static_value(prefix):
        return f"{prefix}:static"

    @classmethod
    def class_value(cls):
        return cls.__name__

    def _private_value(self):
        return f"private:{self.value}"

    def fail_with(self, message):
        raise ValueError(message)


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
                "inherited_value": {"proxy": True, "wrap": True},
                "static_value": {"proxy": True, "wrap": True},
                "class_value": {"proxy": True, "wrap": True},
            },
        )

    def _pre_method_hook(self, method_name, method, args, kwargs):
        self.hook_calls.append(("pre", method_name))

    def _post_method_hook(self, method_name, method, args, kwargs, result):
        self.hook_calls.append(("post", method_name))


class DefaultHintsWrapper(AutoWrapper):
    def __init__(self, target):
        self.hook_calls = []
        self.build_wrapper(target)

    def _pre_method_hook(self, method_name, method, args, kwargs):
        self.hook_calls.append(("pre", method_name))

    def _post_method_hook(self, method_name, method, args, kwargs, result):
        self.hook_calls.append(("post", method_name))


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

    def _pre_method_hook(self, method_name, method, args, kwargs):
        self.hook_calls.append(("pre", method_name))

    def _post_method_hook(self, method_name, method, args, kwargs, result):
        self.hook_calls.append(("post", method_name))


class ExplicitPrivateWrapper(AutoWrapper):
    def __init__(self, target):
        self.hook_calls = []
        self.build_wrapper(
            target,
            hints={"_private_value": {"proxy": True, "wrap": True}},
        )

    def _pre_method_hook(self, method_name, method, args, kwargs):
        self.hook_calls.append(("pre", method_name))

    def _post_method_hook(self, method_name, method, args, kwargs, result):
        self.hook_calls.append(("post", method_name))


class DetailedHookWrapper(AutoWrapper):
    def __init__(self, target):
        self.hook_calls = []
        self.build_wrapper(
            target,
            hints={
                "format_values": {"proxy": True, "wrap": True},
                "fail_with": {"proxy": True, "wrap": True},
            },
        )

    def _pre_method_hook(self, method_name, method, args, kwargs):
        self.hook_calls.append(("pre", method_name, method.__name__, args, kwargs))

    def _post_method_hook(self, method_name, method, args, kwargs, result):
        self.hook_calls.append(
            ("post", method_name, method.__name__, args, kwargs, result)
        )

    def _exception_method_hook(self, method_name, method, args, kwargs, exc):
        self.hook_calls.append(
            ("exception", method_name, method.__name__, args, kwargs, exc)
        )


class InstanceAttributeCollisionWrapper(AutoWrapper):
    def __init__(self, target):
        self.read_value = "already here"
        self.build_wrapper(
            target,
            hints={"read_value": {"proxy": True, "wrap": True}},
        )


class MethodCollisionWrapper(AutoWrapper):
    def __init__(self, target):
        self.build_wrapper(
            target,
            hints={"existing_method": {"proxy": True, "wrap": True}},
        )

    def existing_method(self):
        return "wrapper method"


class CollisionTarget:
    def existing_method(self):
        return "target method"


class AutoWrapperPackagingTests(unittest.TestCase):
    def test_lowercase_import_path_exports_autowrapper(self):
        self.assertIs(LowercaseAutoWrapper, AutoWrapper)

    def test_snake_case_method_discovery_api_matches_compatibility_alias(self):
        snake_case_results = AutoWrapper.get_methods_to_wrap(StatefulTarget)
        compatibility_results = AutoWrapper.getMethods2Wrap(StatefulTarget)

        self.assertEqual(snake_case_results, compatibility_results)
        self.assertIn(
            "read_value",
            [name for name, _method in snake_case_results],
        )


class AutoWrapperBindingTests(unittest.TestCase):
    def test_build_wrapper_rejects_instance_attribute_collision(self):
        target = StatefulTarget()

        with self.assertRaisesRegex(AttributeError, "read_value"):
            InstanceAttributeCollisionWrapper(target)

    def test_build_wrapper_rejects_wrapper_method_collision(self):
        target = CollisionTarget()

        with self.assertRaisesRegex(AttributeError, "existing_method"):
            MethodCollisionWrapper(target)

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

    def test_hints_can_proxy_and_wrap_inherited_methods(self):
        target = StatefulTarget()
        wrapper = RecordingWrapper(target)

        self.assertEqual(wrapper.inherited_value(), "inherited:3")
        self.assertIn(("pre", "inherited_value"), wrapper.hook_calls)
        self.assertIn(("post", "inherited_value"), wrapper.hook_calls)

    def test_no_hints_discovers_inherited_and_direct_methods(self):
        target = StatefulTarget()
        wrapper = DefaultHintsWrapper(target)

        self.assertEqual(wrapper.inherited_value(), "inherited:3")
        self.assertEqual(wrapper.read_value(), 3)

    def test_hints_can_proxy_and_wrap_static_methods(self):
        target = StatefulTarget()
        wrapper = RecordingWrapper(target)

        self.assertEqual(wrapper.static_value("demo"), "demo:static")
        self.assertIn(("pre", "static_value"), wrapper.hook_calls)
        self.assertIn(("post", "static_value"), wrapper.hook_calls)

    def test_hints_can_proxy_and_wrap_class_methods(self):
        target = StatefulTarget()
        wrapper = RecordingWrapper(target)

        self.assertEqual(wrapper.class_value(), "StatefulTarget")
        self.assertIn(("pre", "class_value"), wrapper.hook_calls)
        self.assertIn(("post", "class_value"), wrapper.hook_calls)

    def test_no_hints_discovers_static_and_class_methods(self):
        target = StatefulTarget()
        wrapper = DefaultHintsWrapper(target)

        self.assertEqual(wrapper.static_value("demo"), "demo:static")
        self.assertEqual(wrapper.class_value(), "StatefulTarget")

    def test_no_hints_skips_private_methods_by_default(self):
        target = StatefulTarget()
        wrapper = DefaultHintsWrapper(target)

        self.assertFalse(hasattr(wrapper, "_private_value"))

    def test_explicit_hints_can_proxy_and_wrap_private_methods(self):
        target = StatefulTarget()
        wrapper = ExplicitPrivateWrapper(target)

        self.assertEqual(wrapper._private_value(), "private:3")
        self.assertEqual(
            wrapper.hook_calls,
            [("pre", "_private_value"), ("post", "_private_value")],
        )

    def test_hooks_receive_method_context_args_kwargs_and_result_in_order(self):
        target = StatefulTarget()
        wrapper = DetailedHookWrapper(target)

        self.assertEqual(
            wrapper.format_values("item", value=42, suffix="!"),
            "item:42!",
        )
        self.assertEqual(len(wrapper.hook_calls), 2)
        self.assertEqual(
            wrapper.hook_calls[0],
            (
                "pre",
                "format_values",
                "format_values",
                ("item",),
                {"value": 42, "suffix": "!"},
            ),
        )
        self.assertEqual(
            wrapper.hook_calls[1],
            (
                "post",
                "format_values",
                "format_values",
                ("item",),
                {"value": 42, "suffix": "!"},
                "item:42!",
            ),
        )

    def test_exception_hook_receives_context_and_exception_then_reraises(self):
        target = StatefulTarget()
        wrapper = DetailedHookWrapper(target)

        with self.assertRaisesRegex(ValueError, "boom"):
            wrapper.fail_with("boom")

        self.assertEqual(len(wrapper.hook_calls), 2)
        self.assertEqual(
            wrapper.hook_calls[0][:5],
            ("pre", "fail_with", "fail_with", ("boom",), {}),
        )
        exception_call = wrapper.hook_calls[1]
        self.assertEqual(
            exception_call[:5],
            ("exception", "fail_with", "fail_with", ("boom",), {}),
        )
        self.assertIsInstance(exception_call[5], ValueError)
        self.assertEqual(str(exception_call[5]), "boom")

    def test_wrapped_proxy_preserves_method_metadata(self):
        target = StatefulTarget()
        wrapper = RecordingWrapper(target)

        self.assertEqual(wrapper.format_values.__name__, "format_values")
        self.assertEqual(
            wrapper.format_values.__doc__,
            "Format values for metadata-preservation tests.",
        )
        self.assertIs(wrapper.format_values.__wrapped__.__self__, target)
        self.assertIs(
            wrapper.format_values.__wrapped__.__func__,
            StatefulTarget.format_values,
        )

    def test_direct_proxy_preserves_method_metadata(self):
        target = StatefulTarget()
        wrapper = ConfiguredHintsWrapper(target)

        self.assertEqual(wrapper.read_value.__name__, "read_value")
        self.assertIs(wrapper.read_value.__self__, target)
        self.assertIs(wrapper.read_value.__func__, StatefulTarget.read_value)


if __name__ == "__main__":
    unittest.main()
