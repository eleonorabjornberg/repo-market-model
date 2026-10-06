"""The suite makes no network connection (review finding 9a, #262).

A unit test that reaches a real host depends on mutable external responses and
fails offline. `tests/netguard.py` is imported here, so `unittest discover`
installs it for the whole process: any attempt to resolve or connect to a host
other than the loopback raises `NetworkAccessError`, naming the host. No test
is marked as a network test, and none should be.

Mutation record
---------------
Red first: this file was committed before `tests/netguard.py` existed and
failed at import with `ModuleNotFoundError: No module named 'netguard'`.
Then, in a disposable copy under /tmp with `PYTHONDONTWRITEBYTECODE=1`:

* `if not _is_loopback(host):` -> `if False:` in `_refuse_host` (netguard.py,
  one match by grep) makes `test_a_remote_host_is_refused` fail with
  `NetworkAccessError not raised` (an `AssertionError`).
"""

import socket
import unittest
from pathlib import Path
import urllib.request

import netguard


class NetworkGuardTests(unittest.TestCase):
    def test_a_remote_host_is_refused(self):
        for label, call in (
            ("getaddrinfo", lambda: socket.getaddrinfo("example.com", 443)),
            ("create_connection", lambda: socket.create_connection(("example.com", 443))),
            ("connect", lambda: socket.socket().connect(("93.184.216.34", 443))),
            ("urlopen", lambda: urllib.request.urlopen("https://markets.newyorkfed.org/")),
        ):
            with self.subTest(label):
                with self.assertRaises(netguard.NetworkAccessError) as caught:
                    call()
                self.assertIn("network", str(caught.exception).lower())

    def test_the_loopback_is_not_refused(self):
        # A local server is not the network; the guard must not break one.
        self.assertTrue(netguard._is_loopback("127.0.0.1"))
        self.assertTrue(netguard._is_loopback("localhost"))
        self.assertTrue(netguard._is_loopback("::1"))
        self.assertFalse(netguard._is_loopback("example.com"))
        self.assertFalse(netguard._is_loopback("93.184.216.34"))

    def test_the_guard_is_installed_once(self):
        before = socket.getaddrinfo
        netguard.install()
        self.assertIs(socket.getaddrinfo, before)

    def test_ci_runs_the_suite_with_networking_disabled(self):
        ci = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "tests.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("unshare --net python3 -B -m unittest discover -s tests", ci)


if __name__ == "__main__":
    unittest.main()
