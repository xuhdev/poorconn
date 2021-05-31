# Copyright (C) 2021  Hong Xu <hong@topbug.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

from dataclasses import dataclass
from http.server import HTTPServer, SimpleHTTPRequestHandler
import pathlib
import socket
from socketserver import BaseServer
import threading
from typing import Any, Iterator, no_type_check

import pytest

from poorconn import delay_before_sending_upon_acceptance, make_socket_patchable


# The type of ``config`` is private to pytest
@no_type_check
def pytest_configure(config) -> None:
    # register markers
    config.addinivalue_line(
        "markers", "poorconn_http_server_config(address, port, t, length): Configure fixture ``poorconn_http_server``."
    )


@dataclass(frozen=True)
class Server:
    "The return type of many fixtures. It describes a server object and the URL to access it."
    server: BaseServer
    "A :class:`socketserver.BaseServer` object."
    url: str
    "The URL to the root of :attr:`~.Server.server`."


class _HTTPServer(HTTPServer):
    "Our inherited :class:`HTTPServer` class that allows reusing address."

    allow_reuse_address: bool = True

    def serve_forever_new_thread(self) -> threading.Thread:
        "Serve forever, but in a new thread."

        # [NOTE SO_REUSEADDR]
        # With SO_REUSEADDR, multiple sockets on Windows can listen on the same
        # ports and cause undetermined behaviors. Use SO_EXCLUSIVEADDRUSE to
        # prevent this. See
        # https://docs.microsoft.com/en-us/windows/win32/winsock/using-so-reuseaddr-and-so-exclusiveaddruse
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):  # pragma: no cover, Windows-only
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        else:  # pragma: no cover
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        thread = threading.Thread(target=self.serve_forever, name='Http server on a new thread', daemon=True)
        thread.start()
        return thread


if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):  # pragma: no cover, Windows-only
    _HTTPServer.allow_reuse_address = False
else:  # pragma: no cover
    _HTTPServer.allow_reuse_address = True


class _PoorConnHTTPServerDefault:
    "Default of options for :func:`poorconn_http_server`."

    ADDRESS: str = 'localhost'
    PORT: int = 8080
    T: float = 1
    LENGTH: int = 1024


@pytest.fixture
def poorconn_http_server(tmp_path: pathlib.Path, request: pytest.FixtureRequest) -> Iterator[Server]:
    """A :mod:`pytest` fixture: An :class:`http.server.HTTPServer` object that serves on a new thread. By default, it
    listens on ``localhost:8080``. It's socket is slowed down with :func:`poorconn.delay_before_sending`. It serves
    ``tmp_path`` as the root directory.

    The defaults can be modified by applying the ``@pytest.mark.poorconn_http_server_config`` marker. The marker accepts
    the following parameters:

    - ``address``: The address to bind the HTTP server.
    - ``port``: The port that the HTTP server listens on.
    - ``t``: Same as ``t`` in :func:`poorconn.delay_before_sending`.
    - ``length``: Same as ``length`` in :func:`poorconn.delay_before_sending`.

    Example:

    .. code-block:: python

       @pytest.mark.poorconn_http_server_config(address='127.0.0.1', port=2222, t=2, length=1024)
       def test_http_server(poorconn_http_server, tmp_path):
           "My test..."
    """
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, directory: pathlib.Path = tmp_path, **kwargs: Any):
            # The following type ignore is because of https://github.com/python/mypy/issues/6799
            super().__init__(*args, directory=directory, **kwargs)  # type: ignore[misc]

    # Extract options from markers
    config = request.node.get_closest_marker('poorconn_http_server_config')
    if config is not None:
        options = config.kwargs
    else:
        options = {}
    port = options.get('port', _PoorConnHTTPServerDefault.PORT)
    address = options.get('address', _PoorConnHTTPServerDefault.ADDRESS)
    t = options.get('t', _PoorConnHTTPServerDefault.T)
    length = options.get('length', _PoorConnHTTPServerDefault.LENGTH)

    with _HTTPServer((address, port), Handler) as httpd:
        httpd.socket = make_socket_patchable(httpd.socket)
        delay_before_sending_upon_acceptance(httpd.socket, t=t, length=length)
        thread = httpd.serve_forever_new_thread()
        yield Server(server=httpd, url=f'http://{httpd.server_address[0]}:{httpd.server_address[1]}')
        httpd.shutdown()

    # Wait until httpd has been closed
    thread.join()
