import pathlib
import importlib.util
import unittest
import types
import sys

# tests/testing.py imports requests at module import time; provide a lightweight stub
sys.modules.setdefault("requests", types.SimpleNamespace())

MODULE_PATH = pathlib.Path(__file__).with_name("testing.py")
spec = importlib.util.spec_from_file_location("stockfish_testing", MODULE_PATH)
testing = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(testing)


class DummyProcess:
    def __init__(self):
        self.stdin_closed = False
        self.stdout_closed = False
        self.wait_called = False

        class Stream:
            def __init__(self, close_cb):
                self._close_cb = close_cb

            def close(self):
                self._close_cb()

        self.stdin = Stream(self._close_stdin)
        self.stdout = Stream(self._close_stdout)

    def _close_stdin(self):
        self.stdin_closed = True

    def _close_stdout(self):
        self.stdout_closed = True

    def wait(self):
        self.wait_called = True
        return 7


class TestStockfishClose(unittest.TestCase):
    def test_close_handles_process_with_wait(self):
        stockfish = testing.Stockfish.__new__(testing.Stockfish)
        stockfish.process = DummyProcess()

        result = stockfish.close()

        self.assertEqual(result, 7)
        self.assertTrue(stockfish.process.stdin_closed)
        self.assertTrue(stockfish.process.stdout_closed)
        self.assertTrue(stockfish.process.wait_called)

    def test_close_uses_returncode_when_wait_missing(self):
        stockfish = testing.Stockfish.__new__(testing.Stockfish)
        stockfish.process = type("CompletedLike", (), {"returncode": 0})()

        self.assertEqual(stockfish.close(), 0)


if __name__ == "__main__":
    unittest.main()
