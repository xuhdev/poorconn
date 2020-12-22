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

import pathlib
from socket import socket, SO_REUSEADDR, SOL_SOCKET
import time

import pytest
import requests

from poorconn import delay_before_sending_once, delay_before_sending_upon_acceptance_once, PatchableSocket

import utils


def test_delay_before_sending_once(timeout):
    "Test :func:`poorconn.delay_before_sending_once` and :func:`poorconn.delay_before_sending_upon_acceptance_once`."

    with PatchableSocket() as server_sock:
        server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_sock.bind(('localhost', 7999))
        id_accept = id(server_sock.accept)
        delay_before_sending_upon_acceptance_once(server_sock, t=timeout)

        # Ensure that sending functions of ``server_sock`` has been wrapped
        assert id_accept != id(server_sock.accept)

        with utils.mirror_server_socket_new_thread(server_sock, timeout=timeout):
            with socket() as client_sock:
                client_sock.connect(('localhost', 7999))

                def communicate():
                    sent_content = b'poorconn'
                    starting_time = time.time()
                    client_sock.sendall(sent_content)
                    recved_content = client_sock.recv(128)
                    ending_time = time.time()
                    assert sent_content == recved_content
                    return starting_time, ending_time

                # First time is slow
                starting_time, ending_time = communicate()
                assert ending_time - starting_time > timeout

                # Second time should be quick
                starting_time, ending_time = communicate()
                assert ending_time - starting_time < 1

                # Patch the client side
                client_sock = PatchableSocket.create_from(client_sock)
                id_send = id(client_sock.send)
                delay_before_sending_once(client_sock, t=timeout)
                assert id_send != id(client_sock.send)
                starting_time = time.time()
                num_bytes = client_sock.send(b'a' * 1024)
                ending_time = time.time()
                assert ending_time - starting_time > timeout
                assert 0 < num_bytes <= 1024
                assert client_sock.recv(num_bytes) == num_bytes * b'a'


def test_delay_before_sending_upon_acceptance_once_http_server(http_server, http_url, timeout):
    "Test :func:`poorconn.delay_before_sending_upon_acceptance_once` with ``HTTPServer``."

    patchable_sock = PatchableSocket.create_from(http_server.socket)
    id_accept = id(patchable_sock.accept)
    delay_before_sending_upon_acceptance_once(patchable_sock, t=timeout)
    assert id_accept != id(http_server.socket.accept)  # Ensure that accept() has been wrapped
    http_server.socket = patchable_sock
    utils.httpd_serve_new_thread(http_server)

    with pytest.raises(requests.exceptions.ReadTimeout):
        requests.get(f'{http_url}/setup.py', timeout=timeout * 0.9)

    assert requests.get(f'{http_url}/setup.py').content == pathlib.Path('./setup.py').read_bytes()
