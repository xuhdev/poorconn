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

from contextlib import contextmanager
import socket

from http.server import HTTPServer
import threading


@contextmanager
def echo_server_socket_new_thread(sock: socket.socket, timeout=None):
    """Start a server socket (which has called ``sock.listen()``) in a new thread that accepts a connection, and then
    sends back whatever it receives. It only calls ``sock.accept()`` once.
    """

    stop = False

    def server_socket_work():
        conn, addr = sock.accept()
        conn.settimeout(timeout)
        while not stop:
            try:
                data = conn.recv(1024)
            except socket.timeout:
                continue
            conn.sendall(data)

    thread = threading.Thread(target=server_socket_work, name='Echo socket server', daemon=True)
    thread.start()
    thread.join(timeout=1)
    yield thread
    stop = True
    thread.join()


def httpd_serve_new_thread(httpd: HTTPServer) -> threading.Thread:
    "Let an ``HTTPServer`` object start serve on a new thread."

    thread = threading.Thread(target=httpd.serve_forever, name='Http server on a new thread', daemon=True)
    thread.start()
    thread.join(timeout=1)  # Wait a bit to ensure the server starts up
    return thread


def recv_until(s: socket.socket, num_bytes: int) -> bytes:
    "Call ``s.recv()`` until ``num_bytes`` bytes are received."

    recved_bytes = 0
    content = bytes()
    while recved_bytes < num_bytes:
        new_content = s.recv(num_bytes - recved_bytes)
        recved_bytes += len(new_content)
        content += new_content
    return content


def set_server_socket_options(s: socket.socket) -> None:
    "Set the most common server socket options: SO_EXCLUSIVEADDRUSE on Windows and SO_REUSEADDR on POSIX."

    # See [NOTE SO_REUSEADDR]
    if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):  # Windows-only
        s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    else:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
