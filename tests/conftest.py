# Copyright (C) 2020--2021  Hong Xu <hong@topbug.net>

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


from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import socket
import sys

import pytest


sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

import utils  # noqa: E402


@pytest.fixture
def http_server() -> HTTPServer:
    """A clean HTTPServer object that listens on localhost:8000. It also turns on ``SO_REUSEADDR`` (and also
    ``SO_EXCLUSIVEADDRUSE`` on Windows) for the underlying socket object.
    """

    class _HTTPServer(HTTPServer):
        pass

    # See [NOTE SO_REUSEADDR]
    if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):  # Windows-only
        _HTTPServer.allow_reuse_address = False
    else:
        _HTTPServer.allow_reuse_address = True

    with _HTTPServer(("localhost", 8000), SimpleHTTPRequestHandler) as httpd:
        utils.set_server_socket_options(httpd.socket)
        yield httpd
        httpd.shutdown()


@pytest.fixture
def http_url(http_server) -> str:
    "The root URL of ``http_server``."

    return f'http://{http_server.server_address[0]}:{http_server.server_address[1]}'


@pytest.fixture(scope='session')
def timeout() -> int:
    "How many seconds the test should time out for tests that require a timeout parameter."
    return 2
