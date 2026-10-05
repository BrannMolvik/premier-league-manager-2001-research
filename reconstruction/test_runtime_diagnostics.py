from contextlib import redirect_stderr
from io import StringIO
import unittest

from runtime_diagnostics import TRACE_PREFIX, timed_stage


class RuntimeDiagnosticsTests(unittest.TestCase):
    def test_success_emits_begin_and_end(self):
        stream = StringIO()
        with redirect_stderr(stream):
            with timed_stage("unit.stage"):
                pass
        output = stream.getvalue()
        self.assertIn(f"{TRACE_PREFIX} BEGIN unit.stage", output)
        self.assertIn(f"{TRACE_PREFIX} END unit.stage seconds=", output)

    def test_failure_emits_traceback_and_reraises(self):
        stream = StringIO()
        with self.assertRaisesRegex(ValueError, "boom"):
            with redirect_stderr(stream):
                with timed_stage("unit.failure"):
                    raise ValueError("boom")
        output = stream.getvalue()
        self.assertIn(f"{TRACE_PREFIX} BEGIN unit.failure", output)
        self.assertIn(f"{TRACE_PREFIX} FAIL unit.failure seconds=", output)
        self.assertIn("ValueError: boom", output)
        self.assertIn("Traceback", output)


if __name__ == "__main__":
    unittest.main()
