"""Refuse every network connection in the test process (#262).

Imported by `tests/test_network_guard.py`, so `unittest discover` installs it
before any test runs. A name lookup or a connection to anything but the
loopback raises `NetworkAccessError`; Unix-domain sockets are not the network.
"""

import socket
import urllib.request

_LOOPBACK = {"localhost", "127.0.0.1", "::1", "0.0.0.0", ""}


class NetworkAccessError(RuntimeError):
    """A test tried to reach the network; mock the source instead."""


def _is_loopback(host):
    if host is None:
        return True
    if isinstance(host, bytes):
        host = host.decode("ascii", "replace")
    return host in _LOOPBACK or host.startswith("127.")


def _refuse_host(host, what):
    if not _is_loopback(host):
        raise NetworkAccessError(
            f"network access in a unit test: {what} {host!r}. "
            "Mock the fetcher; no test in this suite may reach the network."
        )


_real_getaddrinfo = socket.getaddrinfo
_real_connect = socket.socket.connect
_real_connect_ex = socket.socket.connect_ex


def _getaddrinfo(host, *args, **kwargs):
    _refuse_host(host, "name lookup of")
    return _real_getaddrinfo(host, *args, **kwargs)


def _target(address):
    return address[0] if isinstance(address, tuple) else None


def _connect(self, address):
    _refuse_host(_target(address), "connection to")
    return _real_connect(self, address)


def _connect_ex(self, address):
    _refuse_host(_target(address), "connection to")
    return _real_connect_ex(self, address)


def install():
    if socket.getaddrinfo is _getaddrinfo:
        return
    # A proxy on the loopback would carry a request out; go direct, so the
    # name lookup of the real host is what the guard sees.
    urllib.request.getproxies = dict
    socket.getaddrinfo = _getaddrinfo
    socket.socket.connect = _connect
    socket.socket.connect_ex = _connect_ex


install()
