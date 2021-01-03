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
from socket import socket
import time

import pytest
import requests

from poorconn import (delay_before_sending,
                      delay_before_sending_once,
                      delay_before_sending_upon_acceptance,
                      delay_before_sending_upon_acceptance_once,
                      PatchableSocket)

import utils


def test_delay_before_sending_once(timeout):
    "Test :func:`poorconn.delay_before_sending_once`."

    with socket() as server_sock:
        utils.set_server_socket_options(server_sock)
        server_sock.bind(('localhost', 7999))
        server_sock.listen()
        # Test the client side
        with utils.echo_server_socket_new_thread(server_sock, timeout=timeout):
            with socket() as client_sock:
                # Patch the client side
                client_sock = PatchableSocket.create_from(client_sock)
                id_send = id(client_sock.send)
                # We use a different and small `t` (<< timeout) here so that `controller.t = timeout_` and its timeout
                # assertions can be more reliably tested
                controller = delay_before_sending_once(client_sock, t=0.1)
                assert timeout != 0.1  # sanity check
                assert controller.t == 0.1
                assert id_send != id(client_sock.send)

                client_sock.connect(('localhost', 7999))

                def test_client(timeout_):
                    controller.reset()
                    controller.t = timeout_
                    # First time
                    starting_time = time.time()
                    num_bytes = client_sock.send(b'a' * 1024)
                    ending_time = time.time()
                    assert ending_time - starting_time > timeout_
                    assert 0 < num_bytes <= 1024
                    assert client_sock.recv(num_bytes) == num_bytes * b'a'

                    # Second time
                    starting_time = time.time()
                    num_bytes = client_sock.send(b'a' * 1024)
                    ending_time = time.time()
                    assert ending_time - starting_time < timeout_ / 5
                    assert 0 < num_bytes <= 1024
                    assert client_sock.recv(num_bytes) == num_bytes * b'a'

                test_client(timeout_=timeout)
                test_client(timeout_=timeout - 0.5)


def test_delay_before_sending_upon_acceptance_once(timeout):
    "Test :func:`poorconn.delay_before_sending_upon_acceptance_once`."

    with PatchableSocket() as server_sock:
        utils.set_server_socket_options(server_sock)
        server_sock.bind(('localhost', 7999))
        id_accept = id(server_sock.accept)
        # We use a different and small `t` (<< timeout) here so that `controller.t = timeout_` and its timeout
        # assertions can be more reliably tested
        controller = delay_before_sending_upon_acceptance_once(server_sock, t=0.1)
        assert timeout != 0.1  # sanity check
        assert controller.t == 0.1

        # Ensure that sending functions of ``server_sock`` has been wrapped
        assert id_accept != id(server_sock.accept)

        server_sock.listen()

        # Test the server side
        def test_server(timeout_):
            with utils.echo_server_socket_new_thread(server_sock, timeout=timeout):
                controller.t = timeout_
                with socket() as client_sock:

                    def communicate():
                        sent_content = b'poorconn'
                        starting_time = time.time()
                        client_sock.sendall(sent_content)
                        recved_content = utils.recv_until(client_sock, len(sent_content))
                        ending_time = time.time()
                        assert sent_content == recved_content
                        return starting_time, ending_time

                    client_sock.connect(('localhost', 7999))

                    # First time is slow
                    starting_time, ending_time = communicate()
                    assert ending_time - starting_time > timeout_

                    # Second time should be quick
                    starting_time, ending_time = communicate()
                    assert ending_time - starting_time < timeout_ / 5

        test_server(timeout_=timeout)
        test_server(timeout_=timeout - 0.5)


@pytest.mark.parametrize('chopped_length', (512, 800, 1024, 1600, 2048))
def test_delay_before_sending(timeout, chopped_length):
    "Test :func:`poorconn.delay_before_sending`. Client always tries to send 1024 bytes every time."

    with socket() as server_sock:
        utils.set_server_socket_options(server_sock)
        server_sock.bind(('localhost', 7999))
        server_sock.listen()

        with utils.echo_server_socket_new_thread(server_sock, timeout=timeout):
            with PatchableSocket() as client_sock:
                client_sock.connect(('localhost', 7999))
                # Patch the client side
                id_send = id(client_sock.send)
                id_sendall = id(client_sock.sendall)
                controller = delay_before_sending(client_sock, t=0.1, length=100)
                # We use a different and small `t` (<< timeout) here so that `controller.t = timeout_` and its timeout
                # assertions can be more reliably tested
                assert timeout != 0.1  # sanity check
                assert chopped_length != 100  # sanity check
                assert controller.t == 0.1
                assert controller.length == 100
                assert id_send != id(client_sock.send)
                assert id_sendall != id(client_sock.sendall)

                controller.t = timeout
                controller.length = chopped_length

                for _ in range(3):  # Run 3 times
                    starting_time = time.time()
                    num_bytes = client_sock.send(b'a' * 1024)
                    ending_time = time.time()
                    assert ending_time - starting_time > timeout
                    assert 0 < num_bytes <= chopped_length
                    assert utils.recv_until(client_sock, num_bytes) == num_bytes * b'a'

                for _ in range(3):  # Run 3 times
                    starting_time = time.time()
                    client_sock.sendall(b'a' * 1024)
                    ending_time = time.time()
                    assert (ending_time - starting_time >
                            timeout * max(1, 1024 // chopped_length + (1024 % chopped_length) > 0))
                    assert utils.recv_until(client_sock, 1024) == 1024 * b'a'


@pytest.mark.parametrize('chopped_length', (512, 800, 1024, 1600, 2048))
def test_delay_before_sending_upon_acceptance(timeout, chopped_length):
    "Test :func:`poorconn.delay_before_sending_upon_acceptance`. Client always tries to send 1024 bytes every time."

    with PatchableSocket() as server_sock:
        utils.set_server_socket_options(server_sock)
        server_sock.bind(('localhost', 7999))
        id_accept = id(server_sock.accept)
        controller = delay_before_sending_upon_acceptance(server_sock, t=0.1, length=100)
        # We use a different and small `t` (<< timeout) here so that `controller.t = timeout_` and its timeout
        # assertions can be more reliably tested
        assert timeout != 0.1  # sanity check
        assert chopped_length != 100  # sanity check
        assert controller.t == 0.1
        assert controller.length == 100

        # Ensure that sending functions of ``server_sock`` has been wrapped
        assert id_accept != id(server_sock.accept)

        server_sock.listen()

        controller.t = timeout
        controller.length = chopped_length

        with utils.echo_server_socket_new_thread(server_sock, timeout=timeout):
            with socket() as client_sock:
                client_sock.connect(('localhost', 7999))

                for _ in range(3):  # Run 3 times
                    sent_content = b'b' * 1024
                    starting_time = time.time()
                    client_sock.sendall(sent_content)
                    recved_content = utils.recv_until(client_sock, len(sent_content))
                    ending_time = time.time()
                    assert sent_content == recved_content
                    assert (ending_time - starting_time >
                            timeout * max(1, 1024 // chopped_length + (1024 % chopped_length) > 0))


def test_delay_before_sending_upon_acceptance_once_http_server(http_server, http_url, timeout):
    "Test :func:`poorconn.delay_before_sending_upon_acceptance_once` with ``HTTPServer``."

    patchable_sock = PatchableSocket.create_from(http_server.socket)
    id_accept = id(patchable_sock.accept)
    delay_before_sending_upon_acceptance_once(patchable_sock, t=timeout)
    assert id_accept != id(http_server.socket.accept)  # Ensure that accept() has been wrapped
    http_server.socket = patchable_sock
    utils.httpd_serve_new_thread(http_server)

    starting_time = time.time()
    content = requests.get(f'{http_url}/setup.py').content
    ending_time = time.time()
    assert ending_time - starting_time > timeout
    assert content == pathlib.Path('./setup.py').read_bytes()

    # Another run
    assert requests.get(f'{http_url}/setup.py').content == pathlib.Path('./setup.py').read_bytes()


@pytest.mark.parametrize('chopped_length', (1600, 2048))
def test_delay_before_sending_upon_acceptance_http_server(http_server, http_url, timeout, chopped_length):
    """Test :func:`poorconn.delay_before_sending_upon_acceptance` with ``HTTPServer``. Client always tries to send 1024
    bytes every time.
    """

    patchable_sock = PatchableSocket.create_from(http_server.socket)
    id_accept = id(patchable_sock.accept)
    delay_before_sending_upon_acceptance(patchable_sock, t=timeout, length=chopped_length)
    assert id_accept != id(http_server.socket.accept)  # Ensure that accept() has been wrapped
    http_server.socket = patchable_sock
    utils.httpd_serve_new_thread(http_server)

    file_size = pathlib.Path('COPYING').stat().st_size
    for _ in range(3):
        starting_time = time.time()
        content = requests.get(f'{http_url}/COPYING').content
        ending_time = time.time()
        assert content == pathlib.Path('COPYING').read_bytes()
        assert ending_time - starting_time > (timeout *
                                              max(1, file_size // chopped_length + (file_size % chopped_length > 0)))
