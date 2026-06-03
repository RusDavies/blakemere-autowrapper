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


class RecordingWrapper(AutoWrapper):
    def __init__(self, target):
        self.hook_calls = []
        self.build_wrapper(
            target,
            hints={
                "read_value": {"proxy": True, "wrap": True},
                "add_to_value": {"proxy": True, "wrap": True},
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


if __name__ == "__main__":
    unittest.main()
