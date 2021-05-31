# Copyright (C) 2020  Hong Xu <hong@topbug.net>

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

from socket import socket

import pytest
import requests

from poorconn import close_upon_acceptance, PatchableSocket

import utils


def test_close_upon_acceptance(timeout):
    "Test :func:`poorconn.close_upon_acceptance` with ``HTTPServer``."

    with PatchableSocket() as server_sock:
        utils.set_server_socket_options(server_sock)
        server_sock.bind(('localhost', 7999))
        id_accept = id(server_sock.accept)
        close_upon_acceptance(server_sock)
        assert id_accept != id(server_sock.accept)  # Ensure that the socket object is wrapped
        server_sock.listen()
        with utils.echo_server_socket_new_thread(server_sock):
            with socket() as client_sock:
                client_sock.connect(('localhost', 7999))
                # EOF should be reached because the other end has closed the socket
                assert len(client_sock.recv(128)) == 0


def test_close_upon_acceptance_http_server(http_server, http_url, timeout):
    "Test :func:`poorconn.close_upon_acceptance` with ``HTTPServer``."

    patchable_sock = PatchableSocket.create_from(http_server.socket)
    id_accept = id(patchable_sock.accept)
    close_upon_acceptance(patchable_sock)
    assert id_accept != id(patchable_sock.accept)  # Ensure that the socket object is wrapped
    http_server.socket = patchable_sock
    utils.httpd_serve_new_thread(http_server)

    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get(f'{http_url}/setup.py', timeout=timeout)
    # We don't assert the content of the exception because, for the client, the error can be anything
    # 'RemoteDisconnected', 'ConnectionResetError', 'ConnectionAbortedError', etc., depending on the progress of the two
    # threads.
