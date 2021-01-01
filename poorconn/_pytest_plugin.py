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

from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
from typing import Iterator

import pytest

from poorconn import delay_before_sending_upon_acceptance, make_socket_patchable


@pytest.fixture(scope='session')
def poorconn_http_server() -> Iterator[HTTPServer]:
    """A simple session-wide HTTPServer object. It listens on localhost:8080 by default. It's socket is slowed down with
    :func:`poorconn.delay_before_sending`.
    """

    with HTTPServer(("localhost", 8080), SimpleHTTPRequestHandler) as httpd:
        httpd.socket = make_socket_patchable(httpd.socket)
        delay_before_sending_upon_acceptance(httpd.socket, t=1, length=1024)
        thread = threading.Thread(target=httpd.serve_forever, name='Http server on a new thread', daemon=True)
        thread.start()
        # Type ignored due to https://github.com/python/typeshed/pull/4882
        # TODO: Remove this type ignore when a new mypy release is out
        yield httpd  # type: ignore
        httpd.shutdown()


@pytest.fixture(scope='session')
def poorconn_http_url(poorconn_http_server: HTTPServer) -> str:
    "The URL to the root of :func:`poorconn_http_server`."

    return f'http://{poorconn_http_server.server_address[0]}:{poorconn_http_server.server_address[1]}'
